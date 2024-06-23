# your_app/consumers.py

import json
from channels.generic.websocket import AsyncWebsocketConsumer
from aiortc import RTCPeerConnection, RTCSessionDescription
from aiortc.contrib.media import MediaPlayer, MediaRelay

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Obtém o nome da sala a partir dos parâmetros da URL
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'chat_{self.room_name}'

        # Adiciona este canal ao grupo da sala
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        # Aceita a conexão WebSocket
        await self.accept()

    async def disconnect(self, close_code):
        # Remove este canal do grupo da sala
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        # Recebe dados do cliente
        data = json.loads(text_data)
        action = data['action']

        # Decide qual função deve ser chamada com base na ação recebida
        if action == 'offer':
            await self.handle_offer(data)
        elif action == 'answer':
            await self.handle_answer(data)
        elif action == 'candidate':
            await self.handle_candidate(data)

    async def handle_offer(self, data):
        # Processa uma oferta (SDP) recebida do cliente
        offer = RTCSessionDescription(sdp=data['sdp'], type=data['type'])

        # Inicializa uma nova conexão peer-to-peer (RTCPeerConnection)
        self.pc = RTCPeerConnection()

        # Adiciona uma faixa de mídia para captura de vídeo
        self.pc.addTrack(MediaPlayer('/dev/video0', format='v4l2', options={'video_size': '640x480'}).video)

        # Define a descrição remota (oferta) recebida
        await self.pc.setRemoteDescription(offer)

        # Cria e define a resposta local (SDP) como descrição local
        answer = await self.pc.createAnswer()
        await self.pc.setLocalDescription(answer)

        # Envia a resposta (SDP) gerada de volta para o cliente
        await self.send(text_data=json.dumps({
            'type': self.pc.localDescription.type,
            'sdp': self.pc.localDescription.sdp
        }))

    async def handle_answer(self, data):
        # Processa uma resposta (SDP) recebida do cliente
        answer = RTCSessionDescription(sdp=data['sdp'], type=data['type'])

        # Define a descrição remota (resposta) recebida
        await self.pc.setRemoteDescription(answer)

    async def handle_candidate(self, data):
        # Processa um candidato ICE (Internet Connectivity Establishment) recebido do cliente
        candidate = data['candidate']

        # Adiciona o candidato ICE à conexão peer-to-peer
        await self.pc.addIceCandidate(candidate)

    async def send_to_group(self, message):
        # Envia uma mensagem para o grupo de sala de chat
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message
            }
        )

    async def chat_message(self, event):
        # Envia uma mensagem de chat para o cliente WebSocket
        message = event['message']
        await self.send(text_data=json.dumps(message))