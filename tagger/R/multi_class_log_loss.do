clear all

insheet using example.csv

program define multi_class_log_loss, rclass
  preserve
  generate loss = y * log(p)
  collapse (sum) loss, by(id)
  summarize loss
  restore
end

multi_class_log_loss
