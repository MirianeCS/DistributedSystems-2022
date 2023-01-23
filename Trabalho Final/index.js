// Sistemas Distribuídos

// Projeto Final - Balanceador de Cargas

// Franciene Bernardi RA: 761851
// Miriane Cardoso Stefanelli RA: 760933


var net = require('net');
var server = net.createServer();  
var balance = -1;
const client = {};

server.on('connection', handleConnection);
server.listen(7000, function() {    
    console.log('Escutando porta -> ', server.address().port); 
    setTimeout(() => {
        initConnection();
    },7000); 
});

async function initConnection(){
    try{
        //conecta service a1
        client['serviceA2'] = new net.Socket();
        client['serviceA2'].on('data', function(data) {
            console.log('Recebeu a mensagem vindo do SERVIÇO: ' + data);
        });
        client['serviceA2'].connect({port:7002, host: 'sd-projeto-final_service_a2_1'});

        //conecta service a2
        client['serviceA1'] = new net.Socket();
        client['serviceA1'].on('data', function(data) {
            console.log('Recebeu a mensagem vindo do SERVIÇO: ' + data);
        });
        client['serviceA1'].connect({port:7001, host: 'sd-projeto-final_service_a1_1'});

        return true;
    }catch(e){
        return false;
    }
}

function handleConnection(socket) {     
  var remoteAddress = socket.remotePort;  
  console.log('Novo cliente -> ', remoteAddress);
  socket.on('data', onSocketData);  
  socket.once('close', onSocketClose);  
  socket.on('error', onSocketError);

  function onSocketData(d) {  
    console.log('mensagem de -> %s: %s', remoteAddress, d.toString());
    let service = loadBalance()
    client[service].write(JSON.stringify({"serviço":"Gravar " ,"data":d.toString()}));

    socket.write(`Recebeu a mensagem vindo do Balanceador: Recebido e salvo em ${service} \n`);
  }
  function onSocketClose() {  
    console.log('conexão encerrado -> ', remoteAddress);  
  }
  function onSocketError(err) {  
    console.log('Conexão %s erro: %s', remoteAddress, err.message);  
  }  
}

function loadBalance(){
    balance = (balance +1) % 2;

    if(balance){
        return 'serviceA2';
    }
    else {
        return 'serviceA1';  
    } 
}