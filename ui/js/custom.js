var myApp = angular.module('myApp', []);

myApp.controller('TargetCtrl', ['$scope', function($scope){
    
    $scope.targetURI = 'http://api.mspray.onalabs.org/targetareas.json';
    $scope.filterText = '2';
    
    $.ajax({
        url: $scope.targetURI,
        type: 'GET',
        success: function(data){
            // pass data to table, filter on demand
            
        }
    });
    
}]);
