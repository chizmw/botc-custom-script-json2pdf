resource "null_resource" "poetry_version" {
  provisioner "local-exec" {
    command = "echo \"{\\\"version\\\":\\\"$(poetry version --short)\\\"}\" > poetry-version.json"
  }
}

data "external" "poetry_version" {
  depends_on = [null_resource.poetry_version]
  program    = ["cat", "poetry-version.json"]
}





resource "null_resource" "commit_version" {
  provisioner "local-exec" {
    command = "echo \"{\\\"version\\\":\\\"$(cd .. && basename $PWD):$(git describe --always --dirty=-dirty)\\\"}\" > commit-version.json"
  }

  triggers = {
    always_run = "${timestamp()}"
  }
}

data "external" "commit_version" {
  depends_on = [null_resource.commit_version]
  program    = ["cat", "commit-version.json"]
}
