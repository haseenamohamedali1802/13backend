from django.shortcuts import render, HttpResponse
import pandas as pd
from datetime import datetime
from .models import Applicant, Connection, Status
from django.views.generic import ListView
from typing import Any
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.utils.dateparse import parse_date
import json
from django.views.decorators.csrf import csrf_exempt
from django.utils.dateparse import parse_date
from django.db.models import Count
from django.db.models.functions import TruncMonth
from django.contrib.auth import authenticate, login as auth_login, logout
def index(request):
    return render(request, "index.html")


def login(request):
    return render(request, "login.html")

def handlelogout(request):
    logout(request)
    return JsonResponse({'message': 'Logged out successfully'})

def uploaddata(request):
    try:
        filepath = "applicant_data_records.csv"
        df = pd.read_csv(filepath, encoding='latin-1')

        status_list = [
            "Rejected",
            "Connection Released",
            "Pending",
            "Approved"
        ]

        for s in status_list:
            Status.objects.get_or_create(Status_Name=s)

        for index, row in df.iterrows():

            applicant, created = Applicant.objects.get_or_create(
                Applicant_Name=row["Applicant_Name"],
                Gender=row["Gender"],
                Districts=row["District"],
                State=row["State"],
                Pincode=int(row["Pincode"]),
                Ownership=row["Ownership"],
                GotId_Type=row["GovtId_Type"],
                Id_Number=str(row["ID_Number"]),
                Category=row["Category"],
            )

            status_value = row.get("Status", "Pending")
            status = Status.objects.get(Status_Name=status_value)

            Date_Of_Application = datetime.strptime(
                str(row["Date_Of_Application"]), "%d-%m-%Y"
            ).strftime("%Y-%m-%d")

            Date_of_Approval = None
            if not pd.isna(row["Date_of_Approval"]):
                Date_of_Approval = datetime.strptime(
                    str(row["Date_of_Approval"]), "%d-%m-%Y"
                ).strftime("%Y-%m-%d")

            Modified_Date = datetime.strptime(
                str(row["Modified_Date"]), "%d-%m-%Y"
            ).strftime("%Y-%m-%d")

            Connection.objects.get_or_create(
                Applicant=applicant,
                Status=status,
                Load_Applied=row["Load_Applied"],
                Date_Of_Application=Date_Of_Application,
                Date_of_Approval=Date_of_Approval,
                Modified_Date=Modified_Date,
                Reviewer_Id=row["Reviewer_Id"],
                Reviewer_Name=row["Reviewer_Name"],
                Reviewer_Comment=row["Reviewer_Comment"],
            )

        return HttpResponse("File uploaded successfully")

    except Exception as e:
        return HttpResponse(f"Error: {e}")

class ConnectionListView(ListView):
    model = Connection
    context_object_name = 'connection'
    paginate_by = 50

    def get_queryset(self):
        queryset = super().get_queryset()
        search_query = self.request.GET.get('search')

        start_date_param = self.request.GET.get('start_date')
        end_date_param = self.request.GET.get('end_date')

        start_date = parse_date(start_date_param) if start_date_param else None
        end_date = parse_date(end_date_param) if end_date_param else None

        if search_query:
            queryset = queryset.filter(Applicant__id__icontains=search_query)

       
        if start_date and end_date:
            queryset = queryset.filter(
                Date_Of_Application__gte=start_date,
                Date_Of_Application__lte=end_date
            )

        return queryset

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('search')
        return context

    def render_to_response(self, context, **response_kwargs):

        serialized_data = [
            {
                'id': conn.id,
                'Load_Applied': conn.Load_Applied,
                'Date_of_Application': conn.Date_Of_Application,
                'Status': conn.Status.Status_Name,
                'Applicant': {
                    'Applicant_Name': conn.Applicant.Applicant_Name,
                    'Gender': conn.Applicant.Gender,
                    'Districts': conn.Applicant.Districts,
                    'State': conn.Applicant.State,
                    'Pincode': conn.Applicant.Pincode,
                    'Ownership': conn.Applicant.Ownership,
                    'GotId_Type': conn.Applicant.GotId_Type,
                    'Id_Number': conn.Applicant.Id_Number,
                    'Category': conn.Applicant.Category,
                },
                'Reviewer_Id': conn.Reviewer_Id,
                'Reviewer_Name': conn.Reviewer_Name,
                'Reviewer_Comment': conn.Reviewer_Comment,
            }
            for conn in context['connection']
        ]

        page_obj = context['page_obj']
        paginator = context['paginator']

        response_data = {
        'data': serialized_data,
        'search_query': context.get('search_query'),
        'total_pages': paginator.num_pages,
        'current_page': page_obj.number,
    }

        return JsonResponse(response_data, json_dumps_params={'indent': 4})
@csrf_exempt 
def update_applicant(request,id):
    if request.method=='GET':
        try:
            applicant=Applicant.objects.get(pk=id)
            connection=Connection.objects.get(Applicant=applicant)
            applicant_data={
                "Applicant_Name":applicant.Applicant_Name,
                "Gender":applicant.Gender,
                "Districts":applicant.Districts,
                "State":applicant.State,
                "Pincode":applicant.Pincode,
                "Ownership":applicant.Ownership,
                "GotId_Type":applicant.GotId_Type,
                "Id_Number":applicant.Id_Number,
                "Category":applicant.Category,
            }
            
            connection_data={
                "Status":connection.Status.Status_Name,
                "Load_Applied":connection.Load_Applied,
                "Date_Of_Application":connection.Date_Of_Application,
                "Date_of_Approval":connection.Date_of_Approval,
                "Modified_Date":connection.Modified_Date,
                "Reviewer_Id":connection.Reviewer_Id,
                "Reviewer_Name":connection.Reviewer_Name,
                "Reviewer_Comment":connection.Reviewer_Comment,
            }
            return JsonResponse({'applicant':applicant_data,'connection':connection_data})
        except Applicant.DoesNotExist:
            return JsonResponse({'error': "Applicant not found"}, status=404)  

        except Connection.DoesNotExist:
            return JsonResponse({'error': "Connection not found"}, status=404)
        
    elif request.method=='POST':
        try:
            applicant=Applicant.objects.get(pk=id)
            connection=Connection.objects.get(Applicant=applicant)
            data=json.loads(request.body)
            status_name=data.get('connection',{}).get('Status')
            status_instance=Status.objects.filter(Status_Name=status_name).first()
            if status_instance:
                applicant_data=data.get('applicant',{})
                for key,value in applicant_data.items():
                    setattr(applicant,key,value)
                    
                applicant.save()
                
                connection_data=data.get('connection',{})
                
                for key,value in connection_data.items():
                    if key != 'Status':
                        if key in ['Date_Of_Application', 'Date_of_Approval', 'Modified_Date'] and value:
                            setattr(connection, key, parse_date(value))  
                        else:
                            setattr(connection, key, value)
                        
                connection.Status = status_instance

                connection.save()
                
                return JsonResponse({'success':'Applicant Details updated successfully'})
            
            else:
                return JsonResponse({'error':'Invalid status value'},status=400)
        except Applicant.DoesNotExist:
            return JsonResponse({'error':'Applicant not found'},status=404)
        except Connection.DoesNotExist:
             return JsonResponse({'error':'Connection not found'},status=404)
        

def connectionvisualization(request):
    connection_requests=Connection.objects.all().values('Date_Of_Application__year','Date_Of_Application__month').annotate(total_requests=Count('id'))
    labels=[f"{x['Date_Of_Application__year']}-{['Date_Of_Application__month']}" for x in connection_requests]
    total_requests=[x['total_requests'] for x in connection_requests]
    
    context={
        'labels':labels,
        'total_requests':total_requests,
    }
    
    return render(request,'connectionvisualization.html',context)

def connectionrequestdata(request):
    selected_status=request.GET.get('status')
    if selected_status:
        filtered_connections=Connection.objects.filter(Status__Status_Name=selected_status)
    else:
         filtered_connections=Connection.objects.all()
         
    data=filtered_connections.annotate(month=TruncMonth('Date_Of_Application')).values('month').annotate(total_requests=Count('id'))
    
    labels=[entry['month'].strftime('%B %Y') for entry in data]
    total_requests=[entry['total_requests'] for entry in data]
    
    return JsonResponse({'labels':labels,'total_requests':total_requests })

@csrf_exempt
def handlelogin(request):
    if request.method == 'POST':
        data = json.loads(request.body)

        print("DATA RECEIVED:", data)

        username = data.get('username')
        password = data.get('password')

        print("USERNAME:", username)
        print("PASSWORD:", password)

        user = authenticate(request, username=username, password=password)

        print("USER:", user)

        if user is not None:
            auth_login(request, user)
            return JsonResponse({'user': user.username}, status=200)
        else:
            return JsonResponse({'error': 'Invalid credentials'}, status=400)

    return JsonResponse({'error': 'Method not allowed'}, status=405)