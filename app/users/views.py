from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.contrib.auth import get_user_model

class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = get_user_model()
        fields = UserCreationForm.Meta.fields + ('email', 'location')

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.status = get_user_model().UserStatus.CREATED
            user.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Účet pro uživatele {username} byl úspěšně vytvořen! Nyní se můžete přihlásit.')
            return redirect('login')
    else:
        form = CustomUserCreationForm()
        
    return render(request, 'users/register.html', {'form': form})