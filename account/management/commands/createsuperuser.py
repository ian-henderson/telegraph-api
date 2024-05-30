from django.contrib.auth.management.commands import createsuperuser


class Command(createsuperuser.Command):
    def get_input_data(self, field, message, default=None):
        if field == "username":
            user_input = input(message).strip()
            while not user_input:
                self.stdout.write("Enter a username.")
                user_input = input(message).strip()
            return user_input
        return super().get_input_data(field, message, default)

    def handle(self, *args, **options):
        options["email"] = options.get("email")
        options["username"] = self.get_input_data(
            "username", message="Username: ", default=options.get("username")
        )

        # username uniqueness check (email uniqueness check is handled automatically)
        while self.UserModel.objects.filter(username=options["username"]).exists():
            self.stderr.write("Error: That username is already taken.")
            options["username"] = self.get_input_data(
                "username", message="Username: ", default=options.get("username")
            )

        super().handle(*args, **options)
