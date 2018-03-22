
(function () {



  //////////////////////////////////

  var app = new Vue({
    //router: null,
    el: '#app',
    data: {
      message: null,
      users: [],

    },
    methods: {

      ///////////////////
      scheduleRefresh: function() {
        let that = this;
        setTimeout(() => {that.handleRefresh()}, 5000 )
      },

      handleRefresh: function() {
        //console.log("handleRefresh")
    
        let that = this;
    
        fetch('/leaderboard.json')
        .then(function(response) {
          return response.json()
    
        }).then(function(json) {
    
          console.log("refresh", json.users.length, "users")
    
          that.users = json.users;
          
          that.scheduleRefresh()

        }).catch(function(ex) {
          console.log('parsing failed', ex)
        })
    
        
      },

    }
  });

  ////////////////

  app.handleRefresh()


})();



