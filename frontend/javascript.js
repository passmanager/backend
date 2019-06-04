var url = "http://gentoo-h:8000/user/"
var password = ""


function getAll() {
  var user = window.location.hash.substr(1);
  $.ajax({
    url: url + user + "/", //gentoo-h je hostname moje masine, treba da stoji domen ovde
    dataType: "json",
    contentType: "text/plain",
    type: "GET",
    async: true,
    success: function(data){
      appendPasswordsList(data)
      $('#loginBoxes').css("display", "none")
      $('#passwordBoxes').css("display", "block")
    },
    error: function(){
      alert("error");
    }
  })
}

function appendPasswordsList(data){
  $(data).each(function(i, single){
    console.log(single)
    $('#passwords').append('<button class="password" onClick="getSingle(\'' + single + '\')">' + single + '</button>')
    $('#passwords').append('<br/>')
  })
}

function getSingle(single){
  var user = window.location.hash.substr(1);
  $.ajax({
    url: url + user + "/" + single, //gentoo-h je hostname moje masine, treba da stoji domen ovde
    dataType: "json",
    contentType: "text/plain",
    type: "GET",
    async: true,
    success: function(data){
      $('#single').empty()
      $('#single').append(data.usernameSalt)
      $('#single').append('<br/>')
      $('#single').append(data.username)
      $('#single').append('<br/>')
      $('#single').append(data.passwordSalt)
      $('#single').append('<br/>')
      $('#single').append(data.password)
      $('#single').append('<br/>')
    },
    error: function(){
      alert("error");
    }
  })
}

function login(){
  var user = $('#username').val()
  window.location = "#" + user
  var pass = $('#password').val()
  //checkIfIsGood
  password = pass;
  getAll();
}

$(document).ready(function(){
  var user = window.location.hash.substr(1);
  $('#username').val(user)
})
