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
        //$("#overview-tab").click();
    }, 1500);

    $(document).on('click', '#submit-button', function(){
        console.log("sending");
    });
});

angular.module("cr_www", [])
    .config(['$httpProvider', function($httpProvidor){
        $httpProvidor.defaults.xsrfCookieName = 'csrftoken';
        $httpProvidor.defaults.xsrfHeaderName = 'X-CSRFToken';
    }])
    .controller("InviteFormCtrl", function($scope, $http, $timeout){

        function reset(){
            $scope.invite = {};
            $scope.formSubmitted = false;
            $scope.serverSuccess = false;
            $scope.serverSuccess = false;
            $scope.invite_form.$setPristine();
            form.removeClass("submitted");
        }

        var modal = angular.element("#invite-modal"),
            form = angular.element("#invite-form");

        modal.on('shown.bs.modal', function (e) {
            reset();
        });

        angular.element("#invite-form").on('submit', function(){
           $scope.formSubmitted = true;
           form.addClass("submitted");
           if($scope.invite_form.$valid){
              $http({
                  method  : 'POST',
                  url     : '/request_beta/',
                  data    : $.param($scope.invite),
                  headers : { 'Content-Type': 'application/x-www-form-urlencoded' }
                })
                .success(function(data, status, headers, config) {
                      console.log("SENT");
                      $scope.serverSuccess = true;
                      $timeout(function(){
                          modal.modal('hide');
                          reset();
                      }, 3500);
                })
                .error(function(data, status, headers, config) {
                      console.log("ERROR");
                      console.log(data);
                      $scope.serverError = false;
                });
           }
           return false;
        });
    });