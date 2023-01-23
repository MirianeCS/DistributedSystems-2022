var net = require('net');
var server = net.createServer();  
const MongoClient = require('mongodb').MongoClient;
const Mensagem = require('./model/mensagens');
var db;

var mongoDB = `mongodb://root:root@${process.env.NAME_DB}:${process.env.MONGO_PORT}`;

MongoClient.connect(mongoDB, (err, client) => {
    if(err){
        throw new Error('Could not connect to the database');
    }
    
    db = client.db("projeto_final");
    console.log('Conectado com sucesso ao Banco de Dados');
})

server.on('connection', handleConnection);
server.listen(process.env.CONTAINER_PORT, function() { 
    console.log('Escutando porta -> ', server.address().port);    
});


function handleConnection(socket) {    
  var remoteAddress = socket.remotePort;  
  console.log("Recebeu a mensagem vindo do Balanceador: Nova solicitação de conexão");
  socket.on('data', onSocketData);  
  socket.once('close', onSocketClose);  
  socket.on('error', onSocketError);
  socket.write(`Conexão estabelecida com o ${process.env.NAME}`); 

  function onSocketData(d) {  
    if(saveMessage(d, remoteAddress))
        socket.write(`Recebido e gravado, em ${process.env.NAME}`);  
    else 
        socket.write(`Erro ao salvar os dados em, ${process.env.NAME}`);  
  }
  function onSocketClose() {  
    console.log('conexão encerrado -> ', remoteAddress);  
  }
  function onSocketError(err) {  
    console.log('Conexão %s erro: %s', remoteAddress, err.message);  
  }  
}

async function saveMessage(data, host){
    let message = new Mensagem();

    try {
        message.host = host;
        message.body = JSON.parse(data).data.toString().replace(/\n/g, '');

        console.log('Serviço : %s , mensagem: %s',JSON.parse(data).serviço, message.body);
    
        db.collection("mensagens").insertOne(message, function(err, res) {
            if (err) throw err;
            console.log("Conteúdo salvo com sucesso\n");
        });
        return true;

    }catch(e){
        return false
    }
}