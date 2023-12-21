$(document).ready(function () {
  $(".dropdown-menu input, .dropdown-menu label").click(function (e) {
    e.stopPropagation();
  });
  $(".selectCountryCode").select2();
  $(".selectField").select2();
  $("input[type='radio']").click(function () {


    if ($("input[name='emp_gender']:checked")) {
      var radioValue = $("input[name='emp_gender']:checked").val();
      $("#emp_gender_" + radioValue).attr("src", "dist/img/svg/" + radioValue + ".svg");
      if (radioValue == 'male') {
        $("#emp_gender_female").attr("src", "dist/img/svg/femalegrey.svg");
        $("#emp_gender_other").attr("src", "dist/img/svg/othergrey.svg");
      } else if (radioValue == 'female') {
        $("#emp_gender_male").attr("src", "dist/img/svg/malegrey.svg");
        $("#emp_gender_other").attr("src", "dist/img/svg/othergrey.svg");
      } else {
        $("#emp_gender_male").attr("src", "dist/img/svg/malegrey.svg");
        $("#emp_gender_female").attr("src", "dist/img/svg/femalegrey.svg");
      }
    }
    if ($("input[name='user_gender']:checked")) {
      var radioValue = $("input[name='user_gender']:checked").val();
      $("#user_gender_" + radioValue).attr("src", "dist/img/svg/" + radioValue + ".svg");
      if (radioValue == 'male') {
        $("#user_gender_female").attr("src", "dist/img/svg/femalegrey.svg");
        $("#user_gender_other").attr("src", "dist/img/svg/othergrey.svg");
      } else if (radioValue == 'female') {
        $("#user_gender_male").attr("src", "dist/img/svg/malegrey.svg");
        $("#user_gender_other").attr("src", "dist/img/svg/othergrey.svg");
      } else {
        $("#user_gender_male").attr("src", "dist/img/svg/malegrey.svg");
        $("#user_gender_female").attr("src", "dist/img/svg/femalegrey.svg");
      }
    }
  });

  $('.add_to_fav').click(function () {
    $(this).toggleClass('checked');
  })

  $(".datepicker").datepicker({
    dateFormat: 'dd/mm/yy',
  });
  $("#datepicker").datepicker("setDate", new Date());

});

function WFModal(modalId, action) {
  if (action == "open") {
    $('#noOfLevels').html('');
    $('#workflow_level_count').val('');
    $("#" + modalId).show();
  }
  if (action == "save") {
    var noLevel = $('#workflow_level_count').val();
    if (noLevel == '') {
      return;
    } else {
      $("#" + modalId).hide();

      if (selectAllType == 'column') {
        selectColCheck(colNo);
        $("#addPermissionModule tbody tr").each(function (index) {
          $("#addPermissionModule tbody tr td:nth-child(" + colNo + ")").children('label').html('Workflow Assigned ' + noLevel);
        });
      } else if (selectAllType == 'row') {
        selectRowCheck(rowNo);
        $("#addPermissionModule tbody tr:nth-child(" + rowNo + ")").each(function (index) {
          $("#addPermissionModule tbody tr:nth-child(" + rowNo + ") td").children('label').html('Workflow Assigned ' + noLevel);
        });
      } else {
        $('#addPermissionModule tbody tr td').find(".singleCheck").next('label').html('Workflow Assigned ' + noLevel);
      }
    }
  }
  if (action == "close") {
    $("#" + modalId).hide();
    if (selectAllType == 'column') {
      $("#addPermissionModule thead tr th:nth-child(" + colNo + ")").children('input').prop("checked", false);
      $("#addPermissionModule thead tr th:nth-child(" + colNo + ")").children('div').removeClass('checked')
      unSelectColCheck(colNo);
    } else if (selectAllType == 'row') {
      $("#addPermissionModule tbody tr:nth-child(" + rowNo + ") th").children('input').prop("checked", false);
      $("#addPermissionModule tbody tr:nth-child(" + rowNo + ") th").children('div').removeClass('checked');
      unSelectRowCheck(rowNo);
    } else {
      $('#addPermissionModule tbody tr td').find(".singleCheck").prev('input').prop("checked", false);
      $('#addPermissionModule tbody tr td').find(".singleCheck").next('label').html('');
      $('#addPermissionModule tbody tr td').find(".singleCheck").removeClass("checked singleCheck");
    }
  }
}

function selectColCheck(colNo) {
  $("#addPermissionModule tbody tr").each(function (index) {
    $("#addPermissionModule tbody tr td:nth-child(" + colNo + ")").children('input').prop("checked", true);
    $("#addPermissionModule tbody tr td:nth-child(" + colNo + ")").children('div').addClass('checked')
    $("#addPermissionModule tbody tr td:nth-child(" + colNo + ")").children('label').addClass('checked');
  });
}

function unSelectColCheck(colNo) {
  $("#addPermissionModule tbody tr").each(function (index) {
    $("#addPermissionModule tbody tr td:nth-child(" + colNo + ")").children('input').prop("checked", false);
    $("#addPermissionModule tbody tr td:nth-child(" + colNo + ")").children('div').removeClass('checked');
    $("#addPermissionModule tbody tr td:nth-child(" + colNo + ")").children('label').removeClass('checked');
  });
}

function selectRowCheck(rowNo) {
  $("#addPermissionModule tbody tr:nth-child(" + rowNo + ")").each(function (index) {
    $("#addPermissionModule tbody tr:nth-child(" + rowNo + ") td").children('input').prop("checked", true);
    $("#addPermissionModule tbody tr:nth-child(" + rowNo + ") td").children('div').addClass('checked')
    $("#addPermissionModule tbody tr:nth-child(" + rowNo + ") td").children('label').addClass('checked')
  });
}

function unSelectRowCheck(rowNo) {
  $("#addPermissionModule tbody tr:nth-child(" + rowNo + ")").each(function (index) {
    $("#addPermissionModule tbody tr:nth-child(" + rowNo + ") td").children('input').prop("checked", false);
    $("#addPermissionModule tbody tr:nth-child(" + rowNo + ") td").children('div').removeClass('checked');
    $("#addPermissionModule tbody tr:nth-child(" + rowNo + ") td").children('label').removeClass('checked');
  });
}

function addWorkflow(level) {
  $('#noOfLevels').html('');
  if (level == 1) {
    $('#noOfLevels').append('<ul class="dots m-0"><li class="green"><div class="row"><div class="col-md-3"><label class="mt-2">Super User</label></div><div class="col-md-5 p-md-0"><input class="inputField" type="text" placeholder="Enter Details" /></div><div class="col-md-4 pr-md-0"><select class="inputField selectField" style="width: 100%;"><option>HR</option></select></div></div></li></ul>');
  } else if (level == 2) {
    $('#noOfLevels').append('<ul class="dots m-0"><li class="green"><div class="row"><div class="col-md-3"><label class="mt-2">Initiate</label></div><div class="col-md-5 p-md-0"><input class="inputField" type="text" placeholder="Enter Details" /></div><div class="col-md-4 pr-md-0"><select class="inputField selectField" style="width: 100%;"><option>HR</option></select></div></div></li><li class="green"><div class="row verticalList"><div class="col-md-3"><label class="mt-2">Approve</label></div><div class="col-md-5 p-md-0"><input class="inputField" type="text" placeholder="Enter Details" /></div><div class="col-md-4 pr-md-0"><select class="inputField selectField" style="width: 100%;"><option>Accounts</option></select></div></div></li></ul>');
  } else if (level > 2 && level <= 10) {
    $('#noOfLevels').append('<ul class="dots m-0"><li class="green"><div class="row"><div class="col-md-3"><label class="mt-2">Initiate</label></div><div class="col-md-5 p-md-0"><input class="inputField" type="text" placeholder="Enter Details" /></div><div class="col-md-4 pr-md-0"><select class="inputField selectField" style="width: 100%;"><option>HR</option></select></div></div></li><li class="green"><div class="row verticalList"><div class="col-md-3"><label class="mt-2">Approve</label></div><div class="col-md-5 p-md-0"><input class="inputField" type="text" placeholder="Enter Details" /></div><div class="col-md-4 pr-md-0"><select class="inputField selectField" style="width: 100%;"><option>Accounts</option></select></div></div></li></ul>');
    var midProcess = level - 2;
    for (var i = 0; i < midProcess; i++) {
      $('#noOfLevels ul').find('li:last').prev().after('<li class="green"><div class="row"><div class="col-md-3"><label id="labelLevel' + i + '" class="mt-2" onclick="showInput(' + i + ')">Forward</label><input type="text" id="inputLevel' + i + '" class="inputField hide" onblur="showLabel(' + i + ')"></div><div class="col-md-5 p-md-0"><input class="inputField" type="text" placeholder="Enter Details"></div><div class="col-md-4 pr-md-0"><select class="inputField selectField" style="width: 100%;"><option>HR</option></select></div></div></li>');
    }
  } else if (level > 10) {
    alert("Out of bounds");
  }
}

function showInput(number) {
  $('#labelLevel' + number).hide();
  $('#inputLevel' + number).val($('#labelLevel' + number).html());
  $('#inputLevel' + number).show();
}
function showLabel(number) {
  if ($('#inputLevel' + number).val() !== '') {
    $('#labelLevel' + number).html($('#inputLevel' + number).val())
  }
  $('#labelLevel' + number).show();
  $('#inputLevel' + number).hide();
}

function setHeightWidth() {
  var containerHeight =
    window.innerHeight -
    ($("#header").outerHeight() + $("#footer").outerHeight()) -
    10;
  $("#containerHeight").height(containerHeight);
}

// ************Toaster************
function openToaster(toastType, message) {
  $("#message").html(message);
  $("#toastBar").attr('class','').addClass('navbar navbar-inverse toastClass');
  if (toastType == "success") {
    $("#toastBar").addClass("toaster-success");
  } else if (toastType == "warning") {
    $("#toastBar").addClass("toaster-warning");
  } else if (toastType == "info" || toastType == 'success alert-success') {
    $("#toastBar").addClass("toaster-info");
  } else if (toastType == "danger" || toastType == 'success alert-danger') {
    $("#toastBar").addClass("toaster-danger");
  }
  $("#toastBar").show().delay(4000).fadeOut();
}

function closeToaster() {
  $("#toastBar").hide();
}

// ************Toaster************
// ************Modal************
function manipulateModal(modalId, action) {
  if (action == "open") {
    $("#" + modalId).show();
    if (modalId == 'addPermissionModal') {
      var mch = $(".modal-AddPermission").height() - $(".modal-header").outerHeight();
      $("#addPermissionModalBody").height(mch);
    }
    if (modalId == 'addUserModal') {
      var mch = $(".modal-AddUser").height() - (($(".modal-header").outerHeight()) + ($("#modalFooter").outerHeight()));
      $("#addUserModalBody").height(mch);
    }
    if (modalId == 'addEmployeeModal') {
      var mch = $(".modal-AddEmployee").height() - (($(".modal-header").outerHeight()) + ($("#modalFooter").outerHeight()));
      $("#addEmpModalBody").height(mch);
    }
    if (modalId == 'viewEmployeeModal') {
      var mch = $(".modal-ViewEmployee").height() - $("#headerViewEmployee").outerHeight();
      $("#viewEmpModalBody").height(mch);
      changeInfoTab('basic')
    }

    if (modalId == 'viewUserModal') {
      var mch = $(".modal-ViewUser").height() - $("#headerViewUser").outerHeight();
      $("#viewUserModalBody").height(mch);
      changeInfoTab('user_basic')
    }


    return;
  }

  if (action == "close") {
    $("#" + modalId).hide();
    $(".modal-backdrop").css("display", "none"); 
    return;
  }
}

function changeInfoTab(showtabId) {
  $("#" + showtabId).addClass("activeTab").siblings().removeClass("activeTab");
  $("#" + showtabId + "Tab").addClass("activeInfoTabs").siblings().removeClass("activeInfoTabs");
}


// var mch =
//     $(".modal-AddEnquiry").height() -
//     ($(".modal-header").outerHeight() +
//         $("#modalFooter").outerHeight());
// $(".modal-body").height(mch);
// ************Modal************

function validateEmail(email) {
  const re = /^([a-zA-Z0-9_\.\-\+])+\@(([a-zA-Z0-9\-])+\.)+([a-zA-Z0-9]{2,4})+$/;
  // if (!re.test(email)) {
  //   // document.getElementById(inputId).value = "";
  //   $("#" + inputId).addClass("border-danger");
  // } else {
  //   if ($("#" + inputId).hasClass("border-danger")) {
  //     $("#" + inputId).removeClass("border-danger");
  //   }
  // }
  return re.test(email);
}

function showLoader() {
  $("#loader").show();
  $("#bodyContainer").addClass('isBlurred');
}

function hideLoader() {
  $("#loader").hide();
  $("#bodyContainer").removeClass('isBlurred');
}

function checkSpecialChar(str) {
  var format = /[!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?]+/;
  if (format.test(str)) {
    return true;
  } else {
    return false;
  }
}

$(document).on('keypress', '.alpha', function (e) {
	return validateAlpha(e) ;
});
$(document).on('keypress', '.alpha_numeric', function (e) {
	return validateAlphaNum(e) ;
});
$(document).on('keypress', '.numeric', function (e) {
	return validateNum(e) ;
});



function validateFloatKeyPress(el, evt) {
  var charCode = (evt.which) ? evt.which : event.keyCode;
  var number = el.value.split('.');
  if (charCode != 46 && charCode > 31 && (charCode < 48 || charCode > 57)) {
    return false;
  }
  if (number.length > 1 && charCode == 46) {
    return false;
  }
  var caratPos = getSelectionStart(el);
  var dotPos = el.value.indexOf(".");
  if (caratPos > dotPos && dotPos > -1 && (number[1].length > 1)) {
    return false;
  }
  return true;
}
function getSelectionStart(o) {
  if (o.createTextRange) {
    var r = document.selection.createRange().duplicate()
    r.moveEnd('character', o.value.length)
    if (r.text == '') return o.value.length
      return o.value.lastIndexOf(r.text)
  } else return o.selectionStart
};

function validateAlphaNum(e) {

	var specialKeys = new Array();
     specialKeys.push(8);  //Backspace
     specialKeys.push(9);  //Tab
     specialKeys.push(46); //Delete
     specialKeys.push(36); //Home
     specialKeys.push(35); //End
     specialKeys.push(37); //Left
     specialKeys.push(39); //Right
     var keyCode = e.keyCode == 0 ? e.charCode : e.keyCode;
     var ret = ((keyCode >= 48 && keyCode <= 57) || (keyCode >= 65 && keyCode <= 90) || keyCode == 32 || (keyCode >= 97 && keyCode <= 122) || (specialKeys.indexOf(e.keyCode) != -1 && e.charCode != e.keyCode));
     return ret;
}

function validateAlpha(e) {
     console.log(e.keyCode)
     var specialKeys = new Array();
     specialKeys.push(8);  //Backspace
     specialKeys.push(9);  //Tab
     specialKeys.push(46); //Delete
     specialKeys.push(36); //Home
     specialKeys.push(35); //End
     specialKeys.push(37); //Left
     specialKeys.push(39); //Right
     var keyCode = e.keyCode == 0 ? e.charCode : e.keyCode;
     var ret = ((keyCode >= 65 && keyCode <= 90) || keyCode == 32 || (keyCode >= 97 && keyCode <= 122) || (specialKeys.indexOf(e.keyCode) != -1 && e.charCode != e.keyCode));
     return ret;
}

function validateNum(e) {

     var specialKeys = new Array();
     specialKeys.push(8);  //Backspace
     specialKeys.push(9);  //Tab
     specialKeys.push(46); //Delete
     specialKeys.push(36); //Home
     specialKeys.push(35); //End
     specialKeys.push(37); //Left
     specialKeys.push(39); //Right
     var keyCode = e.keyCode == 0 ? e.charCode : e.keyCode;
     var ret = ((keyCode >= 48 && keyCode <= 57) || (specialKeys.indexOf(e.keyCode) != -1 && e.charCode != e.keyCode));
     return ret;
}

function validateImageType(id, fileType) {
  for (var i = 0; i < $("#"+id).get(0).files.length; ++i) {
    var file1=$("#"+id).get(0).files[i].name;

    if(file1){                        
      var ext = file1.split('.').pop().toLowerCase(); 
      if($.inArray(ext,['jpg', 'JPG', 'jpeg', 'JPEG', 'png', 'PNG'])===-1){
        swal('Warning', fileType+' Should Be jpg or png', 'warning');
        $("#"+id).val('');
      }else{
        return true;
      }                        
    } else {
      return true; 
    }
  }
}

function validateImageSize(id, fileType) {
  for (var i = 0; i < $("#"+id).get(0).files.length; ++i) {
    var file1=$("#"+id).get(0).files[i].name;

    if(file1){                        
      var file_size=$("#"+id).get(0).files[i].size;
      file_size = Math.round((file_size / 1024));
      if(file_size>5120){
        swal('Warning', fileType+' Size Should Be Upto 5MB', 'warning');
        $("#"+id).val('');
      }else{
        return true;
      }                        
    } else {
      return true; 
    }
  }
}


function sameAbove(formtype) {
  if (formtype == 'emp') {
    var emp_addressLine1_name = document.getElementById('emp_addressLine1_name')
    var emp_addressLine2_name = document.getElementById('emp_addressLine2_name')
    var emp_country_name = document.getElementById('emp_country_name')
    var emp_state_name = document.getElementById('emp_state_name')
    var emp_city_name = document.getElementById('emp_city_name')
    var emp_pinCode_name = document.getElementById('emp_pinCode_name')
    var emp_perm_addressLine1_name = document.getElementById('emp_perm_addressLine1_name');
    var emp_perm_addressLine2_name = document.getElementById('emp_perm_addressLine2_name');
    var emp_perm_country_name = document.getElementById('emp_perm_country_name');
    var emp_perm_state_name = document.getElementById('emp_perm_state_name');
    var emp_perm_city_name = document.getElementById('emp_perm_city_name');
    var emp_perm_pinCode_name = document.getElementById('emp_perm_pinCode_name');

    emp_perm_addressLine1_name.value = emp_addressLine1_name.value
    emp_perm_addressLine2_name.value = emp_addressLine2_name.value
    emp_perm_country_name.value = emp_country_name.value
    emp_perm_state_name.value = emp_state_name.value
    emp_perm_city_name.value = emp_city_name.value
    emp_perm_pinCode_name.value = emp_pinCode_name.value
  } else {
    var addressLine1_name = document.getElementById('addressLine1_name')
    var addressLine2_name = document.getElementById('addressLine2_name')
    var country_name = document.getElementById('country_name')
    var state_name = document.getElementById('state_name')
    var city_name = document.getElementById('city_name')
    var pinCode_name = document.getElementById('pinCode_name')
    var perm_addressLine1_name = document.getElementById('perm_addressLine1_name');
    var perm_addressLine2_name = document.getElementById('perm_addressLine2_name');
    var perm_country_name = document.getElementById('perm_country_name');
    var perm_state_name = document.getElementById('perm_state_name');
    var perm_city_name = document.getElementById('perm_city_name');
    var perm_pinCode_name = document.getElementById('perm_pinCode_name');

    perm_addressLine1_name.value = addressLine1_name.value
    perm_addressLine2_name.value = addressLine2_name.value
    perm_country_name.value = country_name.value
    perm_state_name.value = state_name.value
    perm_city_name.value = city_name.value
    perm_pinCode_name.value = pinCode_name.value
  }
}


// function selectedGender(imageID, gender) {
//   // var radioValue = $("input[name='gender']:checked").val();
//   console.log(imageID);
//   $("#" + imageID + gender).attr("src", "dist/img/svg/" + gender + ".svg")
// }