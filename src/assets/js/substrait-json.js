module.exports = {
  substraitToJson: function (substrait) {
    return JSON.stringify(substrait, null, 2);
  },
};
