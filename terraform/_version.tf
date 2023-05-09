resource "null_resource" "poetry_version" {
  provisioner "local-exec" {
    command = "echo \"{\\\"version\\\":\\\"$(poetry version --short)\\\"}\" > poetry-version.json"
  }
}

data "external" "poetry_version" {
  depends_on = [null_resource.poetry_version]
  program    = ["cat", "poetry-version.json"]
}

output "poetry_version" {
  value = data.external.poetry_version.result.version
}
