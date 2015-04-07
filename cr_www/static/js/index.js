//example js
$(document).ready(function(){

    //tab system
    var activeTab = '';
    $(".feature-tab").each(function(i){
       $(this).click(function(){
           activeTab = $(this).attr("tab-id");
           $(this).addClass("active");
           $(".feature-tab").each(function(i){
              if(activeTab != $(this).attr("tab-id")){
                  $(this).removeClass("active");
              }
           });
       });
    });

    window.setTimeout(function(){
        $("#overview-tab").click();
    }, 1500);
});