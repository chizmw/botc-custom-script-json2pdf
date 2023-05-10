# create an s3 bucket for the generated PDF files
resource "aws_s3_bucket" "botc_pdf_bucket" {
  bucket   = "436158765452-botc-pdf-bucket"
  provider = aws
}

resource "aws_s3_bucket_ownership_controls" "botc_pdf_bucket_ownership_controls" {
  bucket = aws_s3_bucket.botc_pdf_bucket.id
  rule {
    object_ownership = "BucketOwnerPreferred"
  }
}


resource "aws_s3_bucket_acl" "botc_pdf_bucket_acl" {
  depends_on = [
    aws_s3_bucket_ownership_controls.botc_pdf_bucket_ownership_controls
  ]
  bucket = aws_s3_bucket.botc_pdf_bucket.id
  acl    = "private"
}

resource "aws_s3_bucket_versioning" "botc_pdf_bucket_versioning" {
  bucket = aws_s3_bucket.botc_pdf_bucket.id
  versioning_configuration {
    status = "Enabled"
  }
}

###
### DEV
###
resource "aws_s3_bucket" "botc_pdf_bucket_workspaced" {
  bucket   = "436158765452-botc-pdf-bucket-${terraform.workspace}"
  provider = aws
}

resource "aws_s3_bucket_ownership_controls" "botc_pdf_bucket_ownership_controls_workspaced" {
  bucket = aws_s3_bucket.botc_pdf_bucket_workspaced.id
  rule {
    object_ownership = "BucketOwnerPreferred"
  }
}

resource "aws_s3_bucket_acl" "botc_pdf_bucket_acl_workspaced" {
  depends_on = [
    aws_s3_bucket_ownership_controls.botc_pdf_bucket_ownership_controls_workspaced
  ]
  bucket = aws_s3_bucket.botc_pdf_bucket_workspaced.id
  acl    = "private"
}

resource "aws_s3_bucket_versioning" "botc_pdf_bucket_versioning_workspaced" {
  bucket = aws_s3_bucket.botc_pdf_bucket_workspaced.id
  versioning_configuration {
    status = "Enabled"
  }
}
