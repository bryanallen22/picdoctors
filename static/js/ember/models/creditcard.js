attr = DS.attr;

Pd.Creditcard = DS.Model.extend({
  brand:     attr(),
  last4:     attr(),
  exp_month: attr(),
  exp_year:  attr(),
});

