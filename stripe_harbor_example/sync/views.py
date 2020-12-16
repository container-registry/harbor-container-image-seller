from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from sync.models import Customer

from harborclient_light import harborclient

import stripe
stripe.api_key = "sk_test_WCDAe6Ol0ufWlTxkvRw8JhRt00NguuRhXG"

def setup_harbor_client():
    harbor_host = "harbor.container-registry.com"
    harbor_user = "admin_user"
    harbor_pass = "admin_pass"
    return harborclient.HarborClient(
            harbor_host, harbor_user, harbor_pass)

"""
Tasks:
    * for each canceled customer, disable credentials
    * (optional) recurring job - sync to look for new/canceled accounts

"""

def handle_new_subscription(subscription):
  customer = Customer(stripe_id=subscription['customer'])
  customer.save()

def handle_paid_invoice(paid_invoice):
  customer = paid_invoice.customer
  # extend validity date

def handle_deleted_subscription(deleted_subscription):
  customer = deleted_subscription.customer
  # disable credentials

@csrf_exempt
def webhook_handler(request):
  payload = request.body
  event = None

  try:
    event = stripe.Event.construct_from(
      json.loads(payload), stripe.api_key
    )
  except ValueError as e:
    return HttpResponse(status=400)

  if event.type == 'customer.subscription.created':
    new_subscription = event.data.object
    handle_new_subscription(new_subscription)
  elif event.type == 'invoice.paid':
    paid_invoice = event.data.object
    handle_paid_invoice(paid_invoice)
  elif event.type == 'customer.subscription.deleted':
    deleted_subscription = event.data.object
    handle_deleted_subscription(deleted_subscription)
  else:
    print('Unhandled event type {}'.format(event.type))

  return HttpResponse(status=200)

