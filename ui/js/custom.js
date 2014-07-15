var myApp = angular.module('myApp', []);

myApp.controller('TargetCtrl', ['$scope', '$http', function($scope, $http){
    
    $scope.targetURI = 'http://api.mspray.onalabs.org/targetareas.json';
    $scope.filterText = '';
    
    $scope.targetData = [
        {
            'targetId': '1',
            'ranks': '155',
            'houses': 't41',
        },
        {
            'targetId': '2',
            'ranks': '193',
            'houses': 't97',
        }
    ];
    
}]);
