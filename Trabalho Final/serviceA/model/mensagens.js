var mongoose = require('mongoose');
const Schema = mongoose.Schema;

var MensagemModel = new Schema({
    host: {type : String},
    body: {type: String},
},
{ versionKey: false });

module.exports = mongoose.model('Mensagens', MensagemModel )