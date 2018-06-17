from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render

# Create your views here.
from cashier.forms import RechargeForm, BalanceForm


@login_required
def recharge(request):
    form = RechargeForm()

    if request.POST:
        form = RechargeForm(request.POST, cashier=request.user)
        if form.is_valid():
            amount = form.cleaned_data['amount']
            if form.save():
                messages.add_message(request, messages.SUCCESS, "Successfully recharged Rs." + amount)
            else:
                messages.add_message(request, messages.ERROR, "Some error occurred")
            form = RechargeForm()
    return render(request, 'cashier/recharge.html', {"form": form})


@login_required
def view_balance(request):
    form = BalanceForm()
    user = None
    if request.POST:
        form = BalanceForm(request.POST)
        if form.is_valid():
            form = BalanceForm(request.POST)
            user = form.save()

    return render(request, 'cashier/balance.html', {"form": form, 'user': user})
