from users.models import User

for user in User.objects.all():
    user.wallet_address = ''
    user.save()
    user.create_wallet()
