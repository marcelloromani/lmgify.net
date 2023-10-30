import mimetypes

import pulumi
import pulumi_aws as aws
from pulumi import FileAsset, Output, ResourceOptions


def build_public_read_policy_for_bucket(bucket_name):
    return Output.json_dumps({
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": "*",
                "Action": [
                    "s3:GetObject"
                ],
                "Resource": [
                    Output.format("arn:aws:s3:::{0}/*", bucket_name),
                ]
            }
        ]
    }
    )


# Website address
lmgify_net_zone = aws.route53.Zone(
    "lmgify-net-zone",
    comment="HostedZone created by Route53 Registrar",
    name="lmgify.net",
    opts=pulumi.ResourceOptions(protect=True),
)
pulumi.export('zone_id', lmgify_net_zone.id)

# Create s3 bucket to serve static content from
site_s3_bucket = aws.s3.Bucket(
    "lmgify-net",
    website=aws.s3.BucketWebsiteArgs(
        index_document="index.html",
    )
)
pulumi.export('site_s3_bucket', site_s3_bucket.id)
pulumi.export('site_s3_bucket_url', site_s3_bucket.website_endpoint)

# The bucket must be public
public_access_block = aws.s3.BucketPublicAccessBlock(
    'allow-public-access-to-website',
    bucket=site_s3_bucket.id,
    block_public_acls=False,
)

site_s3_bucket_policy = aws.s3.BucketPolicy(
    'allow-public-access-to-website',
    bucket=site_s3_bucket.id,
    policy=build_public_read_policy_for_bucket(site_s3_bucket.id),
    opts=ResourceOptions(
        depends_on=[
            public_access_block,
        ]
    )
)

# copy static content into s3 bucket
file_path = "assets/index.html"
mime_type, _ = mimetypes.guess_type(file_path)
index_obj = aws.s3.BucketObject(
    "index.html",
    bucket=site_s3_bucket.id,
    source=FileAsset(file_path),
    content_type=mime_type,
)

# serve the static S3 content as website
www_site_record = aws.route53.Record(
    "www",
    zone_id=lmgify_net_zone.id,
    name="lmgify.net",
    type="A",
    aliases=[
        aws.route53.RecordAliasArgs(
            name=site_s3_bucket.website_endpoint,
            zone_id=site_s3_bucket.hosted_zone_id,
            evaluate_target_health=False,
        )
    ],
)
