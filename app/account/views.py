import logging

from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.core.mail import EmailMultiAlternatives
from django.db.models import Q
from django.template.loader import get_template
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.status import (
    HTTP_201_CREATED,
    HTTP_400_BAD_REQUEST,
    HTTP_500_INTERNAL_SERVER_ERROR,
)
from rest_framework.views import APIView
from rest_framework.viewsets import ReadOnlyModelViewSet

from .models import PasswordReset
from .serializers import (
    PasswordChangeSerializer,
    PasswordResetSerializer,
    PasswordResetTokenVerificationSerializer,
    UserSerializer,
)


User = get_user_model()


class PasswordChangeView(APIView):
    def post(self, request: Request) -> Response:
        serializer = PasswordChangeSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)

        password = serializer.validated_data.get("password")
        token = serializer.validated_data.get("token")
        reset = PasswordReset.objects.filter(token=token).first()

        if reset is None:
            warning = "Reset record not found for the provided token."
            logging.warning(warning)
            return Response({"warning": warning}, status=HTTP_400_BAD_REQUEST)

        user = User.objects.filter(email=reset.email).first()

        if user is None:
            warning = "User not found."
            logging.warning(warning)
            return Response({"warning": warning}, status=HTTP_400_BAD_REQUEST)

        if not PasswordResetTokenGenerator().check_token(user, token):
            warning = "Invalid token."
            logging.warning(warning)
            return Response({"warning": warning}, status=HTTP_400_BAD_REQUEST)

        reset.delete()
        logging.info(f"Deleted {reset}.")

        user.set_password(password)
        user.save()

        success_message = f"Updated password for {user}."
        logging.info(success_message)

        # Maybe send email notification?

        return Response({"success": success_message})


class PasswordResetView(APIView):
    def post(self, request: Request) -> Response:
        serializer = PasswordResetSerializer(data=request.data)

        if not serializer.is_valid():
            logging.warning(
                f"Invalid data provided to PasswordReset: {serializer.errors}"
            )
            return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)

        user = User.objects.filter(email=serializer.validated_data.get("email")).first()

        if user:
            token_generator = PasswordResetTokenGenerator()
            token = token_generator.make_token(user)
            reset = PasswordReset(email=user.email, token=token)
            reset.save()
            logging.info("Created {reset}.")

            template = get_template("account/reset_password_email.html")
            context = {
                "reset_url": f"localhost:5173/password-change?token={token}",
            }
            html_content = template.render(context)

            email = EmailMultiAlternatives(
                alternatives=((html_content, "text/html"),),
                from_email="no-reply@telegraph.ianhenderson.info",
                subject="Change password for Telegraph",
                to=(user.email,),
            )

            try:
                email.send()
            except Exception as exception:
                error = f"Failed to send password reset email to {user}."
                logging.error(f"{error}: {exception}")
                return Response({"error": error}, status=HTTP_500_INTERNAL_SERVER_ERROR)

            logging.info(f"Sent password reset email to {user}.")

        return Response({"success": "Email was sent if account exists"})


class PasswordResetTokenVerificationView(APIView):
    def post(self, request: Request) -> Response:
        serializer = PasswordResetTokenVerificationSerializer(data=request.data)

        if not serializer.is_valid():
            logging.warning(
                f"Invalid data provided to PasswordResetTokenVerificationView: {serializer.errors}"
            )
            return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)

        token = serializer.validated_data.get("token")
        reset = PasswordReset.objects.filter(token=token).first()

        if reset is None:
            warning = "PasswordReset record not found for token '{token}'."
            logging.warning(warning)
            return Response({"warning": warning}, status=HTTP_400_BAD_REQUEST)

        user = User.objects.filter(email=reset.email).first()

        if not user:
            warning = f"No user found for {reset}."
            logging.warning(warning)
            return Response({"warning": warning}, status=HTTP_400_BAD_REQUEST)

        if not PasswordResetTokenGenerator().check_token(user, token):
            warning = "Invalid token."
            logging.warning(warning)
            return Response({"warning": warning}, status=HTTP_400_BAD_REQUEST)

        logging.info(f"Validated token for {reset}.")

        return Response({"success": "Valid token."})


class UserReadOnlyViewSet(ReadOnlyModelViewSet):
    lookup_field = "username"
    permission_classes = (IsAuthenticated,)
    queryset = User.objects.all()
    serializer_class = UserSerializer

    @action(detail=False, methods=("GET",))
    def search(self, request: Request) -> Response:
        query = request.query_params.get("q", "")
        queryset = User.objects.none()

        if query:
            for part in query.split():
                part_query = (
                    Q(username__icontains=part)
                    | Q(first_name__icontains=part)
                    | Q(last_name__icontains=part)
                )
                queryset |= User.objects.filter(part_query)

        serializer = self.get_serializer(queryset, many=True)
        logging.info(f"User search executed where q='{query}'.")

        return Response(serializer.data)


class UserRegistrationView(APIView):
    def post(self, request: Request) -> Response:
        serializer = UserSerializer(data=request.data)

        if not serializer.is_valid():
            warning = "Invalid data provided to UserRegistration"
            logging.warning(f"{warning}: {serializer.errors}")
            return Response({"warning": warning}, status=HTTP_400_BAD_REQUEST)

        user = serializer.save()
        logging.info(f"Created {user}.")

        return Response(serializer.data, status=HTTP_201_CREATED)
