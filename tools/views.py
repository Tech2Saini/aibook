import json,time,re
from django.contrib.auth.decorators import login_required
from django.shortcuts import render,HttpResponse,redirect
from django.http import JsonResponse
from tools.test import fetch_ai_tool_data
from tools.models import AiTool
from tools.forms import AIToolForm
from django.core.paginator import Paginator
from django.views.generic import ListView
from django.db.models import Q


# Create your views here.
global_paginate_by = 5
global_counts_by = 0

class ToolsViewClass(ListView):

    model = AiTool
    template_name = "index.html"

    paginate_by = global_paginate_by
    context_object_name = 'tools'

    def get_queryset(self):
        global global_counts_by
        context =  super().get_queryset()
        global_counts_by = context.count()
        return context
    # tool = AiTool.objects.all()
    def get_context_data(self, **kwargs):
        global global_counts_by

        context = super().get_context_data(**kwargs)

        paginator = context["paginator"]
        page_obj = context["page_obj"]
        current_page = page_obj.number
        total_pages = paginator.num_pages

        # Generate a custom range: show 2 pages before and after current page
        page_range = list(range(max(1, current_page - 2), min(total_pages + 1, current_page + 3)))
        context["page_range"] = page_range  # Add this to context
        context["counts"] = global_counts_by  # Add this to context
        context["time_v"] = time.time()


        return context

def Category(request,slug):

    return render(request,'qr.html')

def FetchUrlData(request):

    if request.method == "POST":

        url = request.POST.get("url")
        data = fetch_ai_tool_data(url=url)
        data = json.loads(data)
        print("The data is :",data)

        data['paid'] = request.POST.get("paidtool")

        SaveNewTool(data=data,user =request.user)
    return HttpResponse(json.dumps(data))

def Tags(request):
    return redirect("/")

def addToolManual(request):

    if request.method == "POST":
        form = AIToolForm(request.POST, request.FILES)  # Include request.FILES

        if form.is_valid():
            uploaded_file = request.FILES.get('iconfile', None)  # Access file or None
            
            if uploaded_file:
                # Process the uploaded file
                print(f"File received: {uploaded_file.name}")
            else:
                print("No file uploaded.")

            form.save(user=request.user)  # Save if needed
            # return HttpResponse("Form submitted successfully!")

    return redirect("home")

def SaveNewTool(data,user):
    print("Data type is : ",type(data))
    tool = AiTool()
    tool.title = data['title']
    tool.favicon = data['favicon']
    tool.description = data["description"]
    tool.url = data["url"]
    tool.keywords = data["keywords"]
    tool.user = user
    tool.paid = data['paid']

    tool.save()

class SearchTool(ListView):

    model = AiTool
    context_object_name = "tools"
    paginate_by = global_paginate_by
    template_name = "index.html"

    def get_queryset(self):
        global global_counts_by
        context =  super().get_queryset()

        # searching parameters ai tools 
        query = self.request.GET.get('query',None)
        tool_tags = self.request.GET.get('tags',None)

        # filtering parameters ai tools 
        type_sort = self.request.GET.get('type',None)
        _sort = self.request.GET.get('sort',None)
        paid_sort = self.request.GET.get('paid',None)

        
        
        if query is not None:
            context = query_search(self.request)

        elif tool_tags is not None:
            context = context.filter(Q(keywords__icontains=tool_tags))

        elif type_sort is not None:
            context = category_search(self.request)


        if paid_sort is not None:
            context = [tool for tool in context if tool.paid == paid_sort.title()]

        if _sort is not None:
            if _sort in ['t','-t']:
                time_sort = False if _sort == "t" else True
                context = sorted(context,key=lambda k:k.created_at,reverse=time_sort)

            elif _sort in ['n','-n']:
                name_sort = False if _sort == "n" else True
                context = sorted(context,key=lambda k:k.title,reverse=name_sort)

            elif _sort in ['r','-r']:
                rating_sort = False if _sort == "r" else True
                context = sorted(context,key=lambda k:max(k.likes,k.shares),reverse=rating_sort)

            print("The category tools : ",context)

        global_counts_by = len(context)



        return context
    
    def get_context_data(self, **kwargs):
        global global_counts_by
        context =  super().get_context_data(**kwargs)
        context["paid"] = self.request.GET.get('paid',None)
        context["query"] = self.request.GET.get('query',None)
        context["counts"] = global_counts_by
        context["time_v"] = time.time()
        context["tool_tags"] = self.request.GET.get('tags',None)
        context["tool_type"] = self.request.GET.get('type',None)

        return context


def query_search(request):
    query = request.GET.get("query", "").strip()
    if not query:
        return JsonResponse([], safe=False)

    # Fetch all tools
    tools = AiTool.objects.all()
    result_tools = []

    # Tokenize search words (split and remove special characters)
    query_words = re.findall(r'\b\w+\b', query.lower())

    for tool in tools:
        score = 0
        title = tool.title.lower()
        description = tool.description.lower()
        keywords = " ".join(tool.keywords).lower() if tool.keywords else ""

        # Exact match in title (highest weight)
        if query.lower() == title:
            score += 10

        # Check individual words in title, description, and keywords
        for word in query_words:
            if word in title:
                score += 5  # Title match (higher priority)
            if word in description:
                score += 3  # Description match (medium priority)
            if word in keywords:
                score += 2  # Keywords match (lower priority)

        # If there's a match, add tool to results with its score
        if score > 0:
            result_tools.append((tool, score))

    # Sort results based on score (higher scores first)
    result_tools = sorted(result_tools, key=lambda x: x[1], reverse=True)

    return [t for t,_ in result_tools]


def search_suggestions(request):
    query = request.GET.get("q", "").strip().lower()
    if not query:
        return JsonResponse([], safe=False)

    # Tokenize query into words
    query_words = re.findall(r'\b\w+\b', query)

    # Fetch AI tools that contain relevant words in title, keywords, or description
    tools = AiTool.objects.filter(
        Q(title__icontains=query) | Q(description__icontains=query) | Q(keywords__icontains=query)
    )[:10]  # Limit results for efficiency

    suggestions = set()  # Use set to avoid duplicates

    for tool in tools:
        # Extract relevant keywords that match the query
        tool_keywords = ",".join(tool.keywords).lower().split(",") if tool.keywords else []
        for keyword in tool_keywords:
            if any(word in keyword for word in query_words):
                suggestions.add(keyword.strip())

        # Extract relevant sentence fragments from description
        tool_description = tool.description.lower()
        for sentence in re.split(r'[.!?]', tool_description):  # Split by sentence
            if any(word in sentence for word in query_words):

                for s in sentence.replace('/','').strip().split(","):
                    suggestions.add(s.strip())
                    print("Keywords : ",sentence.strip())


    return JsonResponse(json.dumps(list(suggestions)), safe=False)


CATEGORY_MAPPING = {
    "Text generators": ["text", "writing", "generation", "content", "copywriting"],
    "Audio generators": ["audio", "music", "sound", "speech", "song"],
    "Education": ["education", "learning", "tutor", "study", "student"],
    "Automation": ["automation", "workflow", "task", "bot"],
    "Art generators": ["art", "image", "painting", "ai art"],
    "Sound": ["sound", "effects", "noise", "music"],
    "Marketing": ["marketing", "ads", "advertising", "branding"],
    "Video": ["video", "editing", "motion", "cinematic"],
    "Writing": ["writing", "content", "blog", "article"],
    "Chatbot": ["chatbot", "conversation", "chat", "bot"],
    "Design": ["design", "graphic", "logo", "ux"],
    "Productivity": ["productivity", "efficiency", "task", "work"],
    "Animated video": ["animation", "motion", "cartoon", "animated"],
    "🎤 Voice": ["voice", "speech", "narration", "talk"],
}


# Function to classify a tool based on its content
def classify_category(tool):
    """
    Matches title, keywords, and description to a category.
    Returns the best matching category.
    """
    title = tool.title.lower()
    description = tool.description.lower()
    keywords = " ".join(tool.keywords).lower() if tool.keywords else ""

    best_category = None
    best_score = 0

    for category, keywords_list in CATEGORY_MAPPING.items():
        score = sum(title.count(word) + description.count(word) + keywords.count(word) for word in keywords_list)
        if score > best_score:
            best_score = score
            best_category = category

    return best_category

def category_search(request):
    query = request.GET.get("query", "").strip().lower()
    category_filter = request.GET.get("type", "").strip()

    if not query and not category_filter:
        return JsonResponse([], safe=False)
    # Format response
    result_tools = AiTool.objects.all()

    response_data = []
    for tool in result_tools:
        inferred_category = classify_category(tool)

        # Apply category filter if selected
        if category_filter and inferred_category == category_filter:
            response_data.append(tool)

    # print(response_data)
    return response_data
