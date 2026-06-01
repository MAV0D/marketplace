from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.views.decorators.http import require_POST
from django.http import HttpResponse
from django.conf import settings
from datetime import datetime
from listings.models import Listing
from .models import Transaction
from .tokens import transaction_token_generator

@login_required
def order_review(request, listing_id, order_type):
  listing = get_object_or_404(Listing, id=listing_id)
  order_type = int(order_type)
  
  if request.method == "POST":
    new_transaction = Transaction(
      type = Transaction.Type.RENTAL if order_type else Transaction.Type.SALE,
      buyer = request.user,
      listing = listing,
    )
    
    if order_type==1:
      date_range = request.POST.get('date_range')
      
      if date_range and " to " in date_range:
        start_date_str, end_date_str = date_range.split(" to ")
        
        new_transaction.start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
        new_transaction.end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()
      else:
        messages.error(request, "You must enter valid date range (YYYY-MM-DD to YYYY-MM-DD).")
        return render(request, 'transactions/order_page.html', {
          'listing': listing, 
          'order_type': order_type,
        })
      
    new_transaction.save()
    
    if not order_type:
      listing.status = Listing.Status.SOLD
      listing.save()
    
    token = transaction_token_generator.make_token(new_transaction)
    uid = urlsafe_base64_encode(force_bytes(new_transaction.pk))
    
    current_site = request.get_host()
    if not settings.DEBUG:
      current_site += "/marketplace"
    activation_link = f"http://{current_site}/transactions/complete-transaction/{uid}/{token}/"

    
    subject = 'Somebody purchased your item!'
    message = f"Hello {request.user.username},\n"
    if order_type: 
      message+=f"Somebody wahts to purchase your item {listing.name}. Contact them via email {request.user.email} to arrange the details\n"
    else: 
      message+=f"Somebody wahts to rent your item {listing.name} from {new_transaction.start_date} to {new_transaction.end_date}. Contact them via email {request.user.email} to arrange the details\n"
    message += f"""
    After the transaction is done, please confirm it and rate it by clicking this link: {activation_link}
    Thank you for using our Marketplace!
    """
    send_mail(subject, message, 'marketplace@server2.zmatlo.cz', [listing.seller.email])

    
    messages.success(request, "You order was successfully submitted! The seller has been notified and will reach you via email.")
    return redirect('index')
 
  return render(request, 'transactions/order_page.html', {'listing' : listing, 'order_type': order_type})

def complete_transaction(request, uidb64, token):
  try:
    uid = force_str(urlsafe_base64_decode(uidb64))
    transaction = Transaction.objects.get(pk=uid)
  except (TypeError, ValueError, OverflowError, Transaction.DoesNotExist):
    transaction = None

  if transaction is not None and transaction_token_generator.check_token(transaction, token):
    transaction.status = Transaction.Status.CONFIRMED
    transaction.save()
  else:
    messages.error(request, 'The transaction completion link is invalid.')
    return redirect('index')
  
  return render(request, 'transactions/transaction_completion.html', {'transaction': transaction})

@login_required
@require_POST
def rate_transaction(request, transaction_id, rating_value):
  transaction = get_object_or_404(Transaction, id=transaction_id)
  rating_value = int(rating_value)

  if rating_value < 1 or rating_value > 5:
    return HttpResponse("Invalid rating", status=400)

  transaction.seller_rating = rating_value
  transaction.save()

  return render(request, 'transactions/partials/rating_stars.html', {
    'transaction': transaction,
    'already_rated': True,
    'current_rating': rating_value
  })

  
@login_required
@require_POST
def change_transaction_status(request, transaction_id):
  transaction = get_object_or_404(Transaction, id=transaction_id)
  
  # Změníme stav na DONE
  transaction.status = Transaction.Status.CONFIRMED
  transaction.save()
  
  # Vrátíme pouze čistý text nového stavu, kterým HTMX přepíše staré tlačítko
  return HttpResponse(f'<span class="badge bg-success">{transaction.get_status_display()}</span>')