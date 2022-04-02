from django.shortcuts import render, HttpResponse, redirect
from core.models import Evento
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from datetime import datetime, timedelta
from django.http.response import Http404, JsonResponse


# Create your views here.

# def index(request):
#     return redirect('/agenda/')


@login_required(login_url='/login/')
def evento(request, titulo=''):
    if titulo != '':
        consulta = Evento.objects.get(titulo=titulo)
        descricao = Evento.descricao
        return HttpResponse('titulo: {}<br>Consulta: {}<br>Descricao: {}'.format(titulo,consulta,descricao))
    else:
        return HttpResponse('Não é possível realizar consulta! evento não informado')

def login_user(request):
    return render(request, 'login.html')

def logout_user(request):
    logout(request)
    return redirect('/')

def submit_login(request):
    if request.POST:
        username = request.POST.get('username')
        password = request.POST.get('password')
        usuario = authenticate(username=username, password=password)
        if usuario is not None:
            login(request, usuario)
        else:
            messages.error(request, "Usuário ou senha inválido!")
    return redirect('/')


@login_required(login_url='/login/')
def lista_eventos(request):
    usuario = request.user
    data_atual = datetime.now() - timedelta(days=1)
    evento = Evento.objects.filter(fk_usuario=usuario,
                                   data_evento__gt=data_atual) #gt para maior lt para menor
    dados = {'eventos':evento}
    return render(request,'agenda.html',dados)

@login_required(login_url='/login/')
def evento(request):
    id_evento = request.GET.get('id')
    #print(id_evento) # o print será mostrado na guia RUN
    dados = {}
    if id_evento:
        dados['evento'] = Evento.objects.get(id=id_evento)
    return render(request,'evento.html', dados)

@login_required(login_url='/login/')
def submit_evento(request):
    if request.POST:
        titulo = request.POST.get('titulo')
        local = request.POST.get('local')
        data_evento = request.POST.get('data_evento')
        descricao = request.POST.get('descricao')
        usuario = request.user
        id_evento = request.POST.get('id_evento')

        if not id_evento:
            Evento.objects.create(titulo=titulo,
                                  data_evento=data_evento,
                                  local=local,
                                  descricao=descricao,
                                  fk_usuario=usuario)
        else:
            evento = Evento.objects.get(id=id_evento)
            if evento.fk_usuario == usuario:
                evento.titulo = titulo
                evento.data_evento = data_evento
                evento.local = local
                evento.descricao = descricao
                evento.save()

            #Evento.objects.filter(id=id_evento).update(titulo=titulo,
            #                                            data_evento=data_evento,
            #                                            local=local,
            #                                            descricao=descricao)
    return redirect('/')

@login_required(login_url='/login/')
def delete_evento(request, id_evento):
    usuario = request.user
    try:
        evento = Evento.objects.get(id=id_evento)
    except Exception:
        raise Http404()

    if usuario == evento.fk_usuario:
        evento.delete()
    else:
        raise Http404()
    return redirect('/')

@login_required(login_url='/login/')
def jason_lista_evento(request):
    usuario = request.user
    evento = Evento.objects.filter(fk_usuario=usuario).values('id', 'titulo')
    return JsonResponse(list(evento), safe=False)