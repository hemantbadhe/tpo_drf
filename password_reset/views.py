from django.conf import settings
from django.core import signing
from django.core.mail import send_mail
from django.urls import reverse, reverse_lazy

from django.http import Http404
from django.shortcuts import get_object_or_404, redirect
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views import generic
from django.views.decorators.debug import sensitive_post_parameters

try:
    from django.contrib.sites.shortcuts import get_current_site
except ImportError:
    from django.contrib.sites.models import get_current_site
from .forms import PasswordRecoveryForm, PasswordResetForm
from .signals import user_recovers_password
from .utils import get_user_model, get_username
from django.template.loader import render_to_string
import logging

logger = logging.getLogger('promotion')
logger.addHandler(logging.NullHandler())


class SaltMixin(object):
    salt = 'password_recovery'
    url_salt = 'password_recovery_url'


def loads_with_timestamp(value, salt):
    """Returns the unsigned value along with its timestamp, the time when it
    got dumped."""
    try:
        signing.loads(value, salt=salt, max_age=-999999)
    except signing.SignatureExpired as e:
        age = float(str(e).split('Signature age ')[1].split(' >')[0])
        timestamp = timezone.now()
        return timestamp, signing.loads(value, salt=salt)


class RecoverDone(SaltMixin, generic.TemplateView):
    logger.debug("start of recovery done view")
    template_name = 'password_reset/MFS_Reset_Sent.html'

    def get_context_data(self, **kwargs):
        ctx = super(RecoverDone, self).get_context_data(**kwargs)
        try:
            global email_field

            ctx['timestamp'], ctx['email'] = loads_with_timestamp(
                self.kwargs['signature'], salt=self.url_salt
            )

            ctx['email'] = email_field[0]
        except signing.BadSignature:
            raise Http404
        return ctx


recover_done = RecoverDone.as_view()

email_field = ""


class Recover(SaltMixin, generic.FormView):
    logger.debug("start of recover view")
    case_sensitive = True
    form_class = PasswordRecoveryForm
    template_name = 'password_reset/MFS_Recovery_Form.html'
    success_url_name = 'password_reset:password_reset_sent'
    email_template_name = 'password_reset/recovery_email.txt'
    email_subject_template_name = 'password_reset/recovery_email_subject.txt'
    search_fields = ['username', 'email']

    def get_success_url(self):
        return reverse(self.success_url_name, args=[self.mail_signature])

    def get_context_data(self, **kwargs):
        kwargs['url'] = self.request.get_full_path()
        return super(Recover, self).get_context_data(**kwargs)

    def get_form_kwargs(self):
        kwargs = super(Recover, self).get_form_kwargs()
        kwargs.update({
            'case_sensitive': self.case_sensitive,
            'search_fields': self.search_fields,
        })
        return kwargs

    def get_site(self):
        return get_current_site(self.request)

    def send_notification(self):
        context = {
            'site': self.get_site(),
            'user': self.user,
            'username': get_username(self.user),
            'token': signing.dumps(self.user.pk, salt=self.salt),
            'secure': self.request.is_secure(),
        }
        h = self.get_site()

        data = {}

        subject = 'TPO WebApp Login Password Recovery'
        html_content = render_to_string('password_reset/MFS_password_recovery_email.html', context)
        to = [self.user.email]

        global email_field

        # This variable will be access from RecoverDone class to get sender emlai
        email_field = [self.user.email]
        #         print "mail to",str(email_field)
        from_email = settings.EMAIL_HOST_USER
        #         print "mail from",from_email
        send_mail(subject, "", from_email, to, fail_silently=True, html_message=html_content)
        # print "mail",send_mail(subject,"",from_email,to,fail_silently=True, html_message=html_content)

    def form_valid(self, form):
        self.user = form.cleaned_data['user']
        self.send_notification()
        if (
                len(self.search_fields) == 1 and
                self.search_fields[0] == 'username'
        ):
            # if we only search by username, don't disclose the user email
            # since it may now be public information.
            email = self.user.username
        else:
            email = self.user.email
        self.mail_signature = signing.dumps(email, salt=self.url_salt)
        return super(Recover, self).form_valid(form)


recover = Recover.as_view()


class Reset(SaltMixin, generic.FormView):
    logger.debug("start of reset view")
    form_class = PasswordResetForm
    token_expires = None
    template_name = 'password_reset/MFS_Password_Reset.html'
    success_url = reverse_lazy('password_reset:password_reset_done')

    def get_token_expires(self):
        duration = getattr(settings, 'PASSWORD_RESET_TOKEN_EXPIRES',
                           self.token_expires)
        if duration is None:
            duration = 3600 * 48  # Two days
        return duration

    @method_decorator(sensitive_post_parameters('password1', 'password2'))
    def dispatch(self, request, *args, **kwargs):
        self.request = request
        self.args = args
        self.kwargs = kwargs
        self.user = None

        try:
            pk = signing.loads(kwargs['token'],
                               max_age=self.get_token_expires(),
                               salt=self.salt)
        except signing.BadSignature:
            return self.invalid()

        self.user = get_object_or_404(get_user_model(), pk=pk)
        return super(Reset, self).dispatch(request, *args, **kwargs)

    def invalid(self):
        return self.render_to_response(self.get_context_data(invalid=True))

    def get_form_kwargs(self):
        kwargs = super(Reset, self).get_form_kwargs()
        kwargs['user'] = self.user
        return kwargs

    def get_context_data(self, **kwargs):
        ctx = super(Reset, self).get_context_data(**kwargs)
        if 'invalid' not in ctx:
            ctx.update({
                'username': get_username(self.user),
                'token': self.kwargs['token'],
            })
        return ctx

    def form_valid(self, form):
        form.save()
        user_recovers_password.send(
            sender=get_user_model(),
            user=form.user,
            request=self.request
        )
        return redirect(self.get_success_url())


reset = Reset.as_view()


class ResetDone(generic.TemplateView):
    logger.debug("start of reset done view")
    template_name = 'password_reset/MFS_Recovery_Done.html'


reset_done = ResetDone.as_view()

# def password_change(request,user_id):
# #     logger.debug("start of password change view")
#     try:
#         print("INNNNNNNNN")
#         server1 = get_object_or_404(User, pk=user_id)
#         group=Group.objects.get(user=server1)
#
#         if request.method == "POST":
# #             logger.debug(" password change post method")
#             print("dddd")
#             form = PasswordChangeForm(request.POST)
#             if form.is_valid():
# #                 logger.debug("password change form is valid")
#                 user1 = authenticate(username =server1, password=form.cleaned_data['oldPassword'])
#                 if user1 is not None:
# #                    logger.debug("password change form is valid")
#
#                    user1.password=form.cleaned_data['new_password']
#                    user1.set_password(user1.password)
#                    user1.save()
#                    auth_login(request, user1)
#
#
#                    if group.name=="Club":
#                        variables = RequestContext(request,
#                                        {'group':group, 'updatepassword':PasswordChangeForm,'context2': "Your Password has been updated"})
#                        return render(request, 'registration/updateDetails.html', variables)
#
#                 else:
#
#                     variables = RequestContext(request,
#                                        {'group': group, 'updatepassword':PasswordChangeForm,'context2': "Invalid Password"})
#                     if group.name=="Club":
#                        return render(request, 'registration/updateDetails.html', variables)
#
#
#             else:
#
#                 variables = RequestContext(request,
#                                        {'group':group,'updatepassword':PasswordChangeForm,})
#                 if group.name=="Club":
#                        return render(request, 'registration/updateDetails.html', variables)
#
#         else:
#
#             print("get")
#             variables = RequestContext(request,
#                                    {'group':group, 'updatepassword':PasswordChangeForm})
#             if group.name=="Club":
#                    return render(request,'registration/updateDetails.html', variables)
#
#
#     except Exception as e:
#         print(e)
#         render(request,'password_reset/404.html')
