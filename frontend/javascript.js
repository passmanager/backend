var url = "http://gentoo-h:8000/user/"
var password = ""


function getAll() {
  var user = window.location.hash.substr(1);
  passwordHash = sha512(password)
  console.log(sha512(password))
  $.ajax({
    url: url + user, //gentoo-h je hostname moje masine, treba da stoji domen ovde
    dataType: "json",
    contentType: "json;charset=UTF-8",
    data: {"key": passwordHash},
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
  passwordHash = sha512(password)
  $.ajax({
    url: url + user + "/" + single, //gentoo-h je hostname moje masine, treba da stoji domen ovde
    dataType: "json",
    contentType: "json",
    data: {"key": passwordHash},
    type: "GET",
    async: true,
    success: function(data){
      $('#single').empty()
      $('#single').append(passread(data.username, password, data.usernameSalt))
      $('#single').append('<br/>')
      $('#single').append(passread(data.password, password, data.passwordSalt))
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
