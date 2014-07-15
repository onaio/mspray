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
            
            // carry on with map loading functions
            $(document).ready(function(){
                console.log("ajax has completed");
                
                var target_area = $('.target_table a');
        
                target_area.click(function(e){
                    alert("Clicked");
                    
                    var target_id = $(this).attr('href'),
                        target_label = $('.target_label');
                        
                    target_id = target_id.slice(1, target_id.length);
                    target_label.text(target_id);
                    
                    App.loadAreaData(map, target_id);
                });
            });
        });
        targetAreas.error(function(data, status, headers, config) {
            console.log('Sorry, could not retrieve target areas.');
        });
    };
}]);
