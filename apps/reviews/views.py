from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from apps.products.models import Product
from .models import Review
from .forms import ReviewForm

@login_required
def add_review_view(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    existing_review = Review.objects.filter(customer=request.user, product=product).first()

    if request.method == 'POST':
        form = ReviewForm(request.POST, instance=existing_review)
        if form.is_valid():
            review = form.save(commit=False)
            review.customer = request.user
            review.product = product
            review.save()
            messages.success(request, f"Thank you! Your review for {product.name} has been published.")
            return redirect('products:product_detail', slug=product.slug)
    else:
        form = ReviewForm(instance=existing_review)

    return render(request, 'reviews/add_review.html', {
        'product': product,
        'form': form,
        'existing_review': existing_review
    })
