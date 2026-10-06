from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from .models import Product, Category, Wishlist
from .filters import ProductFilter

def home_view(request):
    """
    Modern pharmacy storefront landing page.
    """
    featured_products = Product.objects.filter(active=True, featured=True).select_related('category')[:8]
    latest_medicines = Product.objects.filter(active=True).select_related('category')[:8]
    categories = Category.objects.filter(active=True, parent__isnull=True).prefetch_related('subcategories')[:8]
    
    context = {
        'featured_products': featured_products,
        'latest_medicines': latest_medicines,
        'categories': categories,
    }
    return render(request, 'home.html', context)


def product_list_view(request):
    """
    Medicines & catalog with filter sidebar, sorting, and pagination.
    """
    queryset = Product.objects.filter(active=True).select_related('category')
    
    # Filter
    product_filter = ProductFilter(request.GET, queryset=queryset)
    filtered_qs = product_filter.qs
    
    # Sorting
    sort = request.GET.get('sort', 'latest')
    if sort == 'price_low':
        filtered_qs = filtered_qs.order_by('price')
    elif sort == 'price_high':
        filtered_qs = filtered_qs.order_by('-price')
    elif sort == 'name':
        filtered_qs = filtered_qs.order_by('name')
    else:
        filtered_qs = filtered_qs.order_by('-created_at')
        
    paginator = Paginator(filtered_qs, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    categories = Category.objects.filter(active=True, parent__isnull=True).prefetch_related('subcategories')
    
    context = {
        'filter': product_filter,
        'products': page_obj,
        'page_obj': page_obj,
        'is_paginated': page_obj.has_other_pages(),
        'total_count': filtered_qs.count(),
        'categories': categories,
        'selected_sort': sort,
    }
    return render(request, 'products/product_list.html', context)


def product_detail_view(request, slug):
    """
    Comprehensive product detail with clinical specs, Rx status, batch info, and reviews.
    """
    product = get_object_or_404(
        Product.objects.select_related('category').prefetch_related('additional_images', 'reviews__customer'),
        slug=slug,
        active=True
    )
    related_products = Product.objects.filter(
        category=product.category,
        active=True
    ).exclude(pk=product.pk)[:4]
    
    is_wishlisted = False
    if request.user.is_authenticated:
        is_wishlisted = Wishlist.objects.filter(user=request.user, product=product).exists()
        
    reviews = product.reviews.filter(approved=True).select_related('customer')
    
    context = {
        'product': product,
        'related_products': related_products,
        'is_wishlisted': is_wishlisted,
        'reviews': reviews,
    }
    return render(request, 'products/product_detail.html', context)


def category_list_view(request):
    """
    Browse all categories and subcategories.
    """
    categories = Category.objects.filter(active=True, parent__isnull=True).prefetch_related('subcategories', 'products')
    return render(request, 'products/category_list.html', {'categories': categories})


def category_detail_view(request, slug):
    """
    Show products for a specific category or its descendants.
    """
    category = get_object_or_404(Category, slug=slug, active=True)
    subcategories = category.subcategories.filter(active=True)
    cat_ids = [category.id] + list(subcategories.values_list('id', flat=True))
    
    products_qs = Product.objects.filter(category_id__in=cat_ids, active=True).select_related('category')
    
    paginator = Paginator(products_qs, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'category': category,
        'subcategories': subcategories,
        'products': page_obj,
        'page_obj': page_obj,
        'is_paginated': page_obj.has_other_pages(),
        'total_count': products_qs.count(),
    }
    return render(request, 'products/category.html', context)


def search_view(request):
    """
    Server-side search across name, generic_name, brand, sku, description.
    """
    query = request.GET.get('q', '').strip()
    products_qs = Product.objects.filter(active=True).select_related('category')
    
    if query:
        products_qs = products_qs.filter(
            Q(name__icontains=query) |
            Q(generic_name__icontains=query) |
            Q(brand__icontains=query) |
            Q(sku__icontains=query) |
            Q(description__icontains=query) |
            Q(category__name__icontains=query)
        ).distinct()
        
    paginator = Paginator(products_qs, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'query': query,
        'products': page_obj,
        'page_obj': page_obj,
        'is_paginated': page_obj.has_other_pages(),
        'total_count': products_qs.count(),
    }
    return render(request, 'products/search.html', context)


@login_required
def wishlist_view(request):
    """
    Customer's saved wishlist items.
    """
    items = Wishlist.objects.filter(user=request.user).select_related('product', 'product__category')
    return render(request, 'wishlist/wishlist.html', {'wishlist_items': items})


@login_required
@require_POST
def wishlist_toggle_ajax(request):
    """
    AJAX endpoint to add or remove a product from customer wishlist.
    """
    product_id = request.POST.get('product_id')
    if not product_id:
        return JsonResponse({'success': False, 'message': 'Missing product id'}, status=400)
        
    product = get_object_or_404(Product, pk=product_id)
    wishlist_item = Wishlist.objects.filter(user=request.user, product=product).first()
    
    if wishlist_item:
        wishlist_item.delete()
        action = 'removed'
        is_wishlisted = False
    else:
        Wishlist.objects.create(user=request.user, product=product)
        action = 'added'
        is_wishlisted = True
        
    count = Wishlist.objects.filter(user=request.user).count()
    return JsonResponse({
        'success': True,
        'action': action,
        'is_wishlisted': is_wishlisted,
        'wishlist_count': count,
        'message': f"{product.name} {'added to' if is_wishlisted else 'removed from'} wishlist."
    })
