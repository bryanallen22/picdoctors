attr = DS.attr;

Pd.EmailConfig = DS.Model.extend({
  job_status_change:  attr(),
  jobs_available:     attr(),
  jobs_need_approval: attr(),
  job_reminder:       attr(),
  job_message:        attr(),
  job_rejection:      attr(),
  job_switched:       attr(),
});
