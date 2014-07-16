var myApp = angular.module('myApp', []);

myApp.controller('TargetCtrl', ['$scope', '$http', function($scope, $http){
    
    $scope.districtsURI = 'http://api.mspray.onalabs.org/districts.json';
    $scope.filterText = '';
    $scope.districtData={};
    $scope.targetData={};
    $scope.districtLabel = '';
    $scope.targetLabel = '';
    
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
        
        // update district name
        $scope.districtLabel = district;

        targetAreas.success(function(data, status, headers, config){
            $scope.targetData = data;
        });
        targetAreas.error(function(data, status, headers, config) {
            console.log('Sorry, could not retrieve target areas.');
        });
    };
    
    $scope.loadAreaData = function(targetid){
        //loadAreaData(map);
        
        $scope.targetLabel = targetid;
        
        console.log('TARGET: '+ $scope.targetLabel);
    };
}]);
