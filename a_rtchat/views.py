from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User
from .models import *

class InviteView(APIView):
    """     
     Criação de novas iterações entre clientes    
    """

    # Metodo get recebendo o username
    def get(self, *args, **kwargs):
        """        
         Metodo para a criação de um novo canal caso não exista         
         :returns: JSON Response & HTTP Message
        """
    
        # Cliente o qual vai receber a mensagem
        receiver = self.kwargs['username']
        
        # Resposta para a criação de um chat privado
        response = Response({'detail': 'New channel successfully created'}, status=status.HTTP_201_CREATED)
    
        # Verifica se o usuario cria um chat privado com ele mesmo
        if self.user.username == receiver:
            return Response({'detail': "Can't create channel with yourself"}, status=status.HTTP_400_BAD_REQUEST)
         
        # Objeto dos modelos da pessoa que recebe   
        receiver = User.objects.get(username=receiver)
        
        # Todos os grupos do usuário
        channels = self.request.user.chat_groups(is_private=True)
        
        #Verifica se há algum, caso contrário, ele cria
        if channels.exists():
        
            # Percorre por todos os canais, caso não encontre, ele cria
            for channel in channels:
                if receiver in channel.members.all():                
                    return Response({'detail': 'There is already a connection'}, status=STATUS.HTTP_200_OK)
                    
                else:
                
                    # Criação do canal privado
                    channel = ChatGroup.objects.create(is_private=True)
                    
                    #Adicionando os membros para o canal
                    channel.members.add(receiver, self.request.user)
                    return response
                    
        else:
        
            channel = ChatGroup.objects.create(is_private=True)
            channel.members.add(receiver, self.request.user)
            return response

                
        
        