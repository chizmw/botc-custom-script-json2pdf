
data "external" "useful_version_info" {
  program = ["bash", "${path.module}/get-useful-information.sh"]
}

output "useful_version_info" {
  value = data.external.useful_version_info.result
}
