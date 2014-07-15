var myApp = angular.module('myApp', []);

myApp.controller('TargetCtrl', ['$scope', '$http', function($scope, $http){
    
    $scope.targetURI = 'http://api.mspray.onalabs.org/districts.json';
    $scope.filterText = '';
    
    // $scope.targetData = [
        // {
            // 'targetid': '1',
            // 'ranks': '155',
            // 'houses': 't41',
        // },
        // {
            // 'targetid': '2',
            // 'ranks': '193',
            // 'houses': 't97',
        // }
    // ];
    $scope.targetData={}; 
    
    var getTargetAreas = $http.get($scope.targetURI + '?district=Serenje');

    getTargetAreas.success(function(data, status, headers, config) {
        $scope.targetData = data;
    });
    getTargetAreas.error(function(data, status, headers, config) {
        console.log('Could not retrieve data.');
    });
}]);
