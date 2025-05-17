# documents/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Document, Category
from .forms import DocumentForm, CategoryForm

@login_required
def document_list(request):
    documents = Document.objects.filter(user=request.user)
    categories = Category.objects.all()
    
    category_id = request.GET.get('category')
    if category_id:
        documents = documents.filter(category_id=category_id)
        
    context = {
        'documents': documents,
        'categories': categories
    }
    return render(request, 'documents/document_list.html', context)

@login_required
def upload_document(request):
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            document = form.save(commit=False)
            document.user = request.user
            document.save()
            messages.success(request, 'Document uploaded successfully!')
            return redirect('documents:document_list')
    else:
        form = DocumentForm()
    
    return render(request, 'documents/upload_document.html', {'form': form})

@login_required
def document_detail(request, pk):
    document = get_object_or_404(Document, pk=pk, user=request.user)
    return render(request, 'documents/document_detail.html', {'document': document})

@login_required
def delete_document(request, pk):
    document = get_object_or_404(Document, pk=pk, user=request.user)
    if request.method == 'POST':
        document.file.delete(save=False)  # Delete the actual file
        document.delete()
        messages.success(request, 'Document deleted successfully!')
        return redirect('documents:document_list')
    return render(request, 'documents/delete_document.html', {'document': document})

@login_required
def category_list(request):
    categories = Category.objects.all()
    return render(request, 'documents/category_list.html', {'categories': categories})

@login_required
def create_category(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category created successfully!')
            return redirect('documents:category_list')
    else:
        form = CategoryForm()
    
    return render(request, 'documents/create_category.html', {'form': form})