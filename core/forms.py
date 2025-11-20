from django import forms
from .models import Question, QuestionBank

class QuestionForm(forms.ModelForm):
    correct_answer = forms.ChoiceField(
        choices=[('', 'Select Correct Answer'), ('A', 'A'), ('B', 'B'), ('C', 'C'), ('D', 'D')],
        required=False,
        widget=forms.Select(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md'})
    )
    
    class Meta:
        model = Question
        fields = ['question_text', 'option_a', 'option_b', 'option_c', 'option_d', 'correct_answer']

class QuestionBankForm(forms.ModelForm):
    class Meta:
        model = QuestionBank
        fields = ['subject', 'question_text', 'option_a', 'option_b', 'option_c', 'option_d', 'correct_answer', 'difficulty']
        widgets = {
            'subject': forms.Select(attrs={'class': 'w-full px-3 py-2 border rounded'}),
            'correct_answer': forms.Select(attrs={'class': 'w-full px-3 py-2 border rounded'}),
            'difficulty': forms.Select(attrs={'class': 'w-full px-3 py-2 border rounded'}),
        }
