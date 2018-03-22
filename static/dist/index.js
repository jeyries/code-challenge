
(function () {

// 3. Create the router instance and pass the `routes` option
// You can pass in additional options here, but let's
// keep it simple for now.
const router = new VueRouter({
  routes: [],
  linkActiveClass: "active",
})


  //////////////////////////////////

  

  var app = new Vue({
    router: router,
    el: '#app',
    data: {
      message: null,
      challenges: [],

    },
    methods: {

    }
  });

  //////// some utility functions

  function formatDate(txt) {
      let date = new Date(txt)
      let options = {
        hour12: false,
        weekday: "long",
        year: "numeric",
        month: "long",
        day: "numeric",
        hour: "numeric",
        minute: "numeric"
      }
      return date.toLocaleString('en-US', options);
  }

  ////////

  var indexed = {};
  for (let challenge of CODECHALLENGE.challenges) {
    indexed[challenge.identifier] = challenge;
  }

  app.challenges = CODECHALLENGE.user.records.map( record => {
    let challenge = indexed[record.challenge];

    let status = 'Unknown'
    let when = 'someday'
    switch (record.state) {
      case 'available':
        status = 'Available';
        when = formatDate(record.created_date)
        break;
      case 'done':
        let score = record.score
        let duration = record.duration
        let seconds = duration % 60;
        let minutes = (duration - seconds) / 60;
        status = `Done in ${minutes} minutes and ${seconds} seconds, scoring ${score} points.`
        when = formatDate(record.solved_date)
    }

    return {
      identifier: challenge.identifier,
      title: challenge.title,
      comment: challenge.comment,
      when: when,
      status: status,
    }});

  ///

})();



