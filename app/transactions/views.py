from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.views.decorators.http import require_POST
from django.http import HttpResponse
from django.conf import settings
from datetime import datetime
from listings.models import Listing
from .models import Transaction

@login_required
def order_review(request, listing_id, order_type):
  listing = get_object_or_404(Listing, id=listing_id)
  
  if listing.seller == request.user:
    messages.error(request, "You cannot transact with your own listing.")
    return redirect('listing_detail', id=listing_id)
  
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
    After the transaction is done, please confirm it and rate it in transaction managment panel on your profile ({dashboard_link}): 
    Thank you for using our Marketplace!
    """
    send_mail(subject, message, 'marketplace@server2.zmatlo.cz', [listing.seller.email])

    
    messages.success(request, "You order was successfully submitted! The seller has been notified and will reach you via email.")
    return redirect('index')
 
  return render(request, 'transactions/order_page.html', {'listing' : listing, 'order_type': order_type})

@login_required
def transaction_dashboard(request):
  bought_transactions = Transaction.objects.filter(buyer=request.user).select_related('listing', 'listing__seller').order_by('-date')
  sold_transactions = Transaction.objects.filter(listing__seller=request.user).select_related('listing', 'buyer').order_by('-date')
  
  context = {
    'bought_transactions': bought_transactions,
    'sold_transactions': sold_transactions,
  }
  return render(request, 'transactions/dashboard.html', context)


@login_required
@require_POST
def change_transaction_status(request, transaction_id):
  transaction = get_object_or_404(Transaction, id=transaction_id)
  user = request.user

  if transaction.status == Transaction.Status.PENDING and transaction.listing.seller == user:
    transaction.status = Transaction.Status.CONFIRMED
    transaction.save()
    messages.success(request, "Offer accepted and confirmed.")

  elif transaction.status == Transaction.Status.CONFIRMED and transaction.buyer == user:
    transaction.status = Transaction.Status.DONE
    transaction.save()
    messages.success(request, "Transaction marked as completed!")
    
  return render(request, 'transactions/partials/transaction_row.html', {
    'tx': transaction, 
    'is_seller': transaction.listing.seller == user
  })


@login_required
@require_POST
def rate_transaction(request, transaction_id):
    transaction = get_object_or_404(Transaction, id=transaction_id)
    rating_value = int(request.POST.get('rating', 0))

    if rating_value < 1 or rating_value > 5:
        return HttpResponse("Invalid rating value", status=400)

    if transaction.listing.seller_id == request.user.id:
        transaction.buyer_rating = rating_value
    elif transaction.buyer_id == request.user.id:
        transaction.seller_rating = rating_value
    else:
        return HttpResponse("Unauthorized", status=403)

    transaction.save()

    return render(request, 'transactions/partials/rating_display.html', {
        'rating': rating_value,
    })
    
from django.views.decorators.http import require_POST


