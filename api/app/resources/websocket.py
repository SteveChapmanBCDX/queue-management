from flask import request, g
from flask_socketio import emit, join_room
from jose import jwt

from app.models import CSR
from qsystem import oidc, socketio

@socketio.on('myEvent')
def test_message(message):
    emit('myResponse', {'data': 'got it!', 'count': message['count']})

@socketio.on('joinRoom')
def on_join(message):
    cookie = request.cookies.get("oidc-jwt", None)
    if cookie == None:
        print("cookie is none")
        emit('joinRoomFail', { "sucess": False })
        return

    print(cookie)

    if not oidc.validate_token(cookie):
        print("Cookie failed validation")
        emit('joinRoomFail', { "sucess": False })
        return

    print("Validated")

    claims = unverified_claims = jwt.get_unverified_claims(cookie)
    print(claims)

    username = claims["preferred_username"]
    csr = CSR.query.filter_by(username=username).first()
    if csr:
        print("Joining room")
        join_room(csr.office_id)
        emit('joinRoomSuccess', { "sucess": True })
        emit('update_customer_list', { "sucess": True }, room=csr.office_id)
        print("Success")
    else:
        print("Fail")
        emit('joinRoomFail', { "sucess": False })
