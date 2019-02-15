
from django.contrib import messages
from django.shortcuts import render
from home.models import Teacher
from student.models import Student
from django.shortcuts import redirect
from student.form import StudentForm
from exam.models import Exam
from student.models import StudentMarks
from django.db.models import Max,Sum
import heapq
# Create your views here.
from student.form import StudentMarksForm
def student_detail(request):
    if 'email_id' in request.session:
        teacher=Teacher.objects.get(teacher_email__exact=request.session['email_id'])
        teacher_id=teacher.teacher_id
        student=Student.objects.filter(teacher_id__exact=teacher_id)
        context={'student':student,'teacher':teacher}
        return render(request,'student_detail.html',context)
    else:
        messages.error(request, "Please !! login to your account ")
        return redirect('login')


def addStudent(request):
    if 'email_id' in request.session:
        teacher_id=request.session['id']
        if request.method=='POST':
            stud_form=StudentForm(request.POST or None,request.FILES or None)
            if stud_form.is_valid():
                stud_form.save()
                messages.success(request,"STUDENT ADDED SUCCESSFULLY")
                return redirect('student_detail')
            else:
                messages.error(request,"ERROR OCCURED !!")

                teacher = Teacher.objects.get(teacher_id__exact=teacher_id)
                context={'form':StudentForm(request.POST),'teacher':teacher}
                return render(request,'Manage_student.html',context)

        stud_form=StudentForm(initial={'teacher_id':teacher_id,})
        teacher=Teacher.objects.get(teacher_id__exact=teacher_id)
        context = {'form': stud_form,'teacher':teacher}
        return render(request, 'Manage_student.html', context)
    else:
        messages.error(request, "Please !! login to your account ")
        return redirect('login')

def standard(request,std=0):
    if 'email_id' in request.session:
        teacher = Teacher.objects.get(teacher_email__exact=request.session['email_id'])
        teacher_id = teacher.teacher_id
        std=int(std)
        student = Student.objects.filter(teacher_id__exact=teacher_id,std__exact=std).order_by('rollno')
        context = {'student': student,'std':std }
        return render(request, 'student_detail.html', context)
    else:
        messages.error(request, "Please !! login to your account ")
        return redirect('login')


def entermarks(request,std=0):
    if 'email_id' in request.session:
        if request.method=='POST':
            teacher_id=request.session['id']
            teacher_id=Teacher.objects.get(teacher_id__exact=teacher_id)
            exam_id=request.POST['exam_id']
            exam_id=Exam.objects.get(exam_id__exact=exam_id)
            no_of_stud=int(request.POST['no_of_stud'])
            for i in range(1,no_of_stud+1):
                student_id=Student.objects.get(student_id__exact=request.POST['stud_id'+str(i)])
                x=StudentMarks()
                x.exam_id=exam_id
                x.teacher_id=teacher_id
                x.student_id=student_id
                temp=StudentMarks.objects.filter(student_id__exact=student_id,exam_id__exact=exam_id)
                if temp.count()!=0:
                    messages.success(request,"This exam marks already entered")
                    return redirect('entermark',std)
                t=int(request.POST['m'+str(i)])
                if t!=-1:
                    x.obtain_mark=t
                x.save()
            messages.success(request,"Marks Updated Successfully")
            return redirect('home')
        teacher = Teacher.objects.get(teacher_email__exact=request.session['email_id'])
        teacher_id = teacher.teacher_id
        exam=Exam.objects.filter(teacher_id__exact=teacher_id,std__exact=std).order_by('-exam_date')
        std = int(std)

        student = Student.objects.filter(teacher_id__exact=teacher_id, std__exact=std).order_by('rollno')
        no_of_stud=student.count()
        context = {'student': student, 'teacher': teacher,'exam':exam,'count':exam.count(),'std':std,'no_of_stud':no_of_stud}
        return render(request, 'student_marks.html', context)
    else:
        messages.error(request, "Please !! login to your account ")
        return redirect('login')



def student_graph(request,std=0,student_id=0):
    if 'email_id' in request.session:
        teacher_id = request.session['id']
        std = int(std)
        student_id = int(student_id)
        subject = {'1': 'HINDI', '2': 'MARATHI', '3': 'HISTORY', '4': 'GEOGRAPHY', '5': 'MATH', '6': 'SCIENCE'}
        report = {}
        for i in range(1, 7):
            exam = Exam.objects.filter(std=std, subject=subject[str(i)], teacher_id__exact=teacher_id)
            marks = StudentMarks.objects.filter(exam_id__in=exam, student_id__exact=student_id,
                                                teacher_id__exact=teacher_id)
            marks = marks.aggregate(Sum('obtain_mark'))
            m = marks.get("obtain_mark__sum")
            obtain_mark = m
            if obtain_mark is None:
                total_mark = None
                percentage = None
            else:
                total_marks = exam.aggregate(Sum('total_mark'))
                total_mark = total_marks.get("total_mark__sum")
                percentage = (obtain_mark * 100) / total_mark
                percentage = round(percentage, 2)
            sub = subject[str(i)]
            if percentage is not None:
                if percentage < 70:
                    color = "red"
                elif percentage == 70:
                    color = "yellow"
                else:
                    color = "green"
            else:
                color = "blue"
            report[i] = {'subject': sub, 'percentage': percentage, 'obtain_mark': obtain_mark, 'total_mark': total_mark,
                         'color': color, }
            i = i + 1
        stud = Student.objects.get(student_id__exact=student_id)
        context = {'report': report, 'stud': stud, 'x': 360,'std':std,'student_id':stud.student_id}
        return render(request, 'graph.html', context)
    else:
        messages.error(request, "Please !! login to your account ")
        return redirect('login')

def detail_report(request,std=0,student_id=0):
    if 'email_id' in request.session:
        teacher_id = request.session['id']
        std=int(std)
        student_id=int(student_id)
        subject={'1':'HINDI','2':'MARATHI','3':'HISTORY','4':'GEOGRAPHY','5':'MATH','6':'SCIENCE'}
        report={}
        for i in range(1,7):
            exam=Exam.objects.filter(std=std,subject=subject[str(i)],teacher_id__exact=teacher_id)
            marks = StudentMarks.objects.filter(exam_id__in=exam, student_id__exact=student_id,
                                                teacher_id__exact=teacher_id)
            marks = marks.aggregate(Sum('obtain_mark'))
            m = marks.get("obtain_mark__sum")
            obtain_mark = m
            if obtain_mark is None:
                total_mark=None
                percentage=None
            else:
                total_marks = exam.aggregate(Sum('total_mark'))
                total_mark = total_marks.get("total_mark__sum")
                percentage = (obtain_mark * 100) / total_mark
                percentage = round(percentage, 2)
            sub=subject[str(i)]
            if percentage is not None:
                if percentage<70:
                    color="pink"
                elif percentage==70:
                    color="yellow"
                else:
                    color="green"
            else:
                color="blue"
            report[i]={'subject':sub,'percentage':percentage,'obtain_mark':obtain_mark,'total_mark':total_mark,'color':color,}
            i=i+1
        stud=Student.objects.get(student_id__exact=student_id)
        context={'report':report,'stud':stud,'std':std,'student_id':student_id}
        return render(request, 'student_report.html',context)
    else:
        messages.error(request, "Please !! login to your account ")
        return redirect('login')
def report(request,std=0):
    hint=None
    if 'email_id' in request.session:
        std=int(std)
        teacher_id=request.session['id']
        if std!=0:
            student_id = Student.objects.filter(teacher_id__exact=teacher_id,std__exact=std)
        else:
            student_id = Student.objects.filter(teacher_id__exact=teacher_id,)
            hint="dis"

        i=1
        report={}
        for s in student_id:
            student_id=s.student_id
            roll_no=s.rollno
            fname=s.fname
            lname=s.lname
            stand=s.std
            stud=StudentMarks.objects.filter(student_id=s.student_id,obtain_mark__isnull=False)
            marks=stud.aggregate(Sum('obtain_mark'))
            m=marks.get("obtain_mark__sum")
            obtain_mark=m
            if obtain_mark is None:
                total_mark=None
                percentage=None
            else:
                total_mark=0
                for eid in stud:
                    exam = Exam.objects.filter(exam_id=int(eid.exam_id_id),teacher_id__exact=teacher_id,std__exact=stand)
                    total_marks = exam.aggregate(Sum('total_mark'))
                    total_mark =total_mark+ total_marks.get("total_mark__sum")

                percentage = (obtain_mark * 100) / total_mark
                percentage = round(percentage, 2)
            report[i]={'std':stand,'student_id':student_id,'roll_no':roll_no,'fname':fname,'lname':lname,'obtain_mark':obtain_mark,'total_mark':total_mark,'percentage':percentage}
            i=i+1

        context={'report':report,'std':std,'count':i,'hint':hint}
        return render(request, 'report.html', context)
    else:
        messages.error(request, "Please !! login to your account ")
        return redirect('login')

def rank(request,std=0,student_id=0):
    if 'email_id' in request.session:
        std=int(std)
        teacher_id=request.session['id']
        sid = int(student_id)
        student_id=Student.objects.filter(teacher_id__exact=teacher_id,std__exact=std,)
        i=1

        report={}
        for s in student_id:
            student_id=s.student_id
            roll_no=s.rollno
            fname=s.fname
            lname=s.lname
            img = s.img
            school_name = s.school_name
            stud=StudentMarks.objects.filter(student_id=s.student_id,obtain_mark__isnull=False)
            marks=stud.aggregate(Sum('obtain_mark'))
            m=marks.get("obtain_mark__sum")
            obtain_mark=m
            if obtain_mark is None:
                total_mark=None
                percentage=None
            else:
                total_mark = 0
                for eid in stud:
                    exam = Exam.objects.filter(exam_id=int(eid.exam_id_id), teacher_id__exact=teacher_id,std__exact=std)
                    total_marks = exam.aggregate(Sum('total_mark'))
                    total_mark = total_mark + total_marks.get("total_mark__sum")
                percentage = (obtain_mark * 100) / total_mark
                percentage = round(percentage, 2)
            if percentage is not None:
                if percentage<70:
                    color="pink"
                elif percentage==70:
                    color="yellow"
                else:
                    color="green"
            else:
                color="blue"
                percentage=0
                total_mark=0
            report[i]={'color':color,'img':img,'school_name':school_name,'student_id':student_id,'roll_no':roll_no,'fname':fname,'lname':lname,'obtain_mark':obtain_mark,'total_mark':total_mark,'percentage':percentage}
            i=i+1
        stud=Student.objects.get(student_id__exact=sid)
        x=max(float((d['percentage'])) for d in report.values())

        p=sorted(report,key=lambda x:(report[x]['percentage']),reverse=True)
        r=report
        repor={}
        j=1

        for i in p:
            repor[j]=report[i]

            j=j+1

        context={'report':repor,'std':std,'count':i,'student_id':sid,'stud':stud,'max':x,"rem":"blue"}
        return render(request, 'rank.html', context)
    else:
        messages.error(request, "Please !! login to your account ")
        return redirect('login')


def rank_graph(request,std=0,student_id=0):
    if 'email_id' in request.session:
        std=int(std)
        teacher_id=request.session['id']
        sid = int(student_id)
        student_id=Student.objects.filter(teacher_id__exact=teacher_id,std__exact=std)
        i=1

        report={}
        for s in student_id:
            student_id = s.student_id
            roll_no = s.rollno
            fname = s.fname
            lname = s.lname
            img = s.img
            school_name = s.school_name
            stud = StudentMarks.objects.filter(student_id=s.student_id,obtain_mark__isnull=False)
            marks = stud.aggregate(Sum('obtain_mark'))
            m = marks.get("obtain_mark__sum")
            obtain_mark = m
            if obtain_mark is None:
                total_mark = None
                percentage = None
            else:
                total_mark = 0
                for eid in stud:
                    exam = Exam.objects.filter(exam_id=int(eid.exam_id_id), teacher_id__exact=teacher_id,std__exact=std)
                    total_marks = exam.aggregate(Sum('total_mark'))
                    total_mark = total_mark + total_marks.get("total_mark__sum")
                percentage = (obtain_mark * 100) / total_mark
                percentage = round(percentage, 2)
            if percentage is not None:
                if percentage < 70:
                    color = "red"
                elif percentage == 70:
                    color = "yellow"
                else:
                    color = "green"
            else:
                color = "blue"
                percentage = 0
                total_mark = 0
            report[i]={'color':color,'img':img,'school_name':school_name,'student_id':student_id,'roll_no':roll_no,'fname':fname,'lname':lname,'obtain_mark':obtain_mark,'total_mark':total_mark,'percentage':percentage}
            i=i+1
        stud=Student.objects.get(student_id__exact=sid)
        x=max(float(d['percentage']) for d in report.values())

        p=sorted(report,key=lambda x:(report[x]['percentage']),reverse=True)
        r=report
        repor={}
        j=1
        for i in p:
            repor[j]=report[i]
            j=j+1

        context={'report':repor,'std':std,'count':i,'student_id':sid,'stud':stud,'max':x,'rem':"blue"}
        return render(request, 'rank_graph.html', context)
    else:
        messages.error(request, "Please !! login to your account ")
        return redirect('login')