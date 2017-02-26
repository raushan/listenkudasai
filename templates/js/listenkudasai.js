$(".js-watch-button").on('click', getVideo);
$(".js-show-advanced-search").on('click', showAdvancedSearch);
$(".js-submit-vid-button").on('click', validateVideoForm);
$(".js-submit-advanced").on('click', getVideoAdvanced);
$(".js-clear-advanced").on('click', clearAdvancedSearch);
$(".js-report-vid").on('click', reportVideo);

$(document).ready(function(){
  setTimeout(function(){
    $('.alert').hide('slow');
  }, 5000);
  getVideo();
  $('[data-toggle="tooltip"]').tooltip();
})

function getVideo(){
  $.ajax({
    type: "GET",
    url: "/video",
    dataType: 'json',
  })
  .done(function( data ) {
    if(data['status'] == 'success'){
      $('div.embed-responsive').empty().html(data['video_html']);
      $('.js-no-vids').hide();
      $($('.js-report-vid input[type=hidden]')[0]).val(data["video_id"]);
    }else{
      $('div.embed-responsive').empty();
      $('.js-no-vids').removeClass("hide");
    }
  });
}

function validateVideoForm(e){
  e.preventDefault();
  url = $('input#urlinput').val();
  numCategories = $(".js-submit-form input[type=checkbox]:checked").length;
  //tags = $('input#tagsinput').val();
  if(url === '' || numCategories == 0){
    bootbox.alert("Please fill out all required fields, indicated by an asterisk");
  }else{
    $(".js-submit-form").submit();
  }
}

function getVideoAdvanced(e){
  e.preventDefault();
  var categories = [];
  $("#advancedform :checked").each(function() {
      categories.push($(this).val());
  });
  if(categories.length == 0){
    bootbox.alert("please choose a category");
    return;
  }
  $.ajax({
    type: "POST",
    url: "/advanced",
    dataType: "json",
    data: {'list' : categories},
  })
  .done(function( data ) {
    if(data['status'] == 'success'){
      $('.js-watch-button').off('click').on('click', getVideoAdvanced);
      $('.js-no-vids-adv').addClass("hide");
      $('div.embed-responsive').empty().html(data['video_html']);
      $('p.browsing-info').html("You are currently browsing the categories: ".concat(data['categories']));
    }else{
      $('.js-watch-button').off('click').on('click', getVideo);
      $('div.embed-responsive').empty();
      $('.js-no-vids-adv').removeClass("hide");
      $('p.browsing-info').empty();
    }
  });
}

function showAdvancedSearch(){
  $("#advanced-search-form").removeClass("hide");
}

function clearAdvancedSearch(){
  $('.js-watch-button').off('click').on('click', getVideo);
  $("#advanced-search-form").addClass("hide");
  $('.js-no-vids-adv').addClass("hide");
  $('p.browsing-info').empty();
}

function reportVideo(e){
  e.preventDefault();
  bootbox.confirm("Report non working video or inappopriate content?", function(result){
    if(result){
      $(".js-report-vid").submit();
    }
  });
}
