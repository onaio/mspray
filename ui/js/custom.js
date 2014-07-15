var myApp = angular.module('myApp', []);

myApp.controller('TargetCtrl', ['$scope', '$http', function($scope, $http){
    
    $scope.districtsURI = 'http://api.mspray.onalabs.org/districts.json';
    $scope.filterText = '';
    $scope.districtData={};
    $scope.targetData={};
    
    // get districts
    var getDistricts = $http.get($scope.districtsURI);

    getDistricts.success(function(data, status, headers, config) {
        $scope.districtData = data;
    });
    getDistricts.error(function(data, status, headers, config) {
        console.log('Sorry, could not retrieve districts.');
    });
    
    // get target areas
    $scope.getTargetAreas = function(district){
        var districtUrl = $scope.districtsURI + '?district=' + district;
        
        var targetAreas = $http.get(districtUrl);

        targetAreas.success(function(data, status, headers, config) {
            $scope.targetData = data;
        });
        targetAreas.error(function(data, status, headers, config) {
            console.log('Sorry, could not retrieve target areas.');
        });
    };
}]);
