# AWS Configuration Guide

This document provides detailed AWS configuration requirements for the Infrastructure Repo Backup tool.

## Table of Contents
- [Overview](#overview)
- [For Cloud Administrators](#for-cloud-administrators)
- [For Backup Tool Users](#for-backup-tool-users)
- [Permission Details](#permission-details)
- [Security Best Practices](#security-best-practices)
- [Troubleshooting](#troubleshooting)

## Overview

The backup tool uses AWS S3 for storage with two distinct permission levels:

1. **Setup Permissions** - Required once to create infrastructure (bucket, IAM user, policies)
2. **Backup Permissions** - Required for daily backup operations (read/write to S3 only)

**Important**: The tool does NOT require AWS administrator access. It only needs specific, limited permissions.

## For Cloud Administrators

This section helps AWS administrators set up appropriate permissions for users who need to run the backup tool.

### Option 1: Create IAM Policy for Setup Users

If you want users to run the `--setup` command themselves, create this IAM policy:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "S3BucketManagement",
      "Effect": "Allow",
      "Action": [
        "s3:CreateBucket",
        "s3:PutBucketVersioning",
        "s3:PutBucketEncryption",
        "s3:PutBucketPublicAccessBlock",
        "s3:PutBucketLifecycleConfiguration",
        "s3:PutBucketTagging",
        "s3:PutBucketPolicy",
        "s3:GetBucketLocation",
        "s3:ListBucket"
      ],
      "Resource": [
        "arn:aws:s3:::repo-backup-*",
        "arn:aws:s3:::*-repo-backup"
      ]
    },
    {
      "Sid": "IAMUserManagement",
      "Effect": "Allow",
      "Action": [
        "iam:CreateUser",
        "iam:CreateAccessKey",
        "iam:PutUserPolicy",
        "iam:AttachUserPolicy",
        "iam:CreatePolicy",
        "iam:TagUser"
      ],
      "Resource": [
        "arn:aws:iam::*:user/repo-backup-*",
        "arn:aws:iam::*:policy/repo-backup-*"
      ]
    },
    {
      "Sid": "IdentityVerification",
      "Effect": "Allow",
      "Action": [
        "sts:GetCallerIdentity"
      ],
      "Resource": "*"
    }
  ]
}
```

**Policy Name Suggestion**: `RepoBackupSetupPermissions`

**To attach this policy to a user or group:**

1. Go to IAM Console > Policies > Create Policy
2. Use JSON editor and paste the above policy
3. Name it `RepoBackupSetupPermissions`
4. Attach to users or groups who need to run setup

### Option 2: Administrator Runs Setup (Recommended)

**Recommended approach**: Administrators run the setup once and provide backup credentials to users.

1. Administrator runs:
   ```bash
   repo-backup s3 --setup --bucket-name company-repo-backup
   ```

2. Setup creates:
   - S3 bucket with versioning, encryption, lifecycle policies
   - IAM user `repo-backup-user` with minimal S3 permissions
   - Access keys for the backup user

3. Administrator provides to backup user:
   - Bucket name
   - AWS Access Key ID
   - AWS Secret Access Key
   - AWS region

4. Backup user adds to `.env.local`:
   ```bash
   AWS_PROFILE=repo-backup  # Or use keys directly
   AWS_ACCESS_KEY_ID=AKIA...
   AWS_SECRET_ACCESS_KEY=...
   AWS_REGION=us-east-1
   S3_BUCKET_NAME=company-repo-backup
   ```

### Restricting Bucket Names

To enforce naming conventions, modify the policy's `Resource` section:

```json
"Resource": [
  "arn:aws:s3:::mycompany-repo-backup-*"
]
```

### Service Control Policies (SCPs)

For AWS Organizations, you can enforce that only specific buckets can be created:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Deny",
      "Action": [
        "s3:CreateBucket"
      ],
      "Resource": "*",
      "Condition": {
        "StringNotLike": {
          "s3:prefix": [
            "mycompany-repo-backup-*",
            "repo-backup-*"
          ]
        }
      }
    }
  ]
}
```

## For Backup Tool Users

### Scenario 1: You Have Setup Permissions

If your administrator gave you setup permissions, run:

```bash
# Basic setup
repo-backup s3 --setup

# With custom bucket name
repo-backup s3 --setup --bucket-name my-company-backups

# With Glacier for cost savings
repo-backup s3 --setup --enable-glacier

# With specific AWS profile
repo-backup s3 --setup --setup-profile my-aws-profile
```

The setup will:
1. Create S3 bucket with proper configuration
2. Create IAM user `repo-backup-user`
3. Generate access keys
4. Display credentials (save these to `.env.local`)

### Scenario 2: Administrator Provides Credentials

If your administrator ran setup and gave you credentials:

1. Copy `.env.example` to `.env.local`:
   ```bash
   cp .env.example .env.local
   ```

2. Add AWS credentials to `.env.local`:
   ```bash
   AWS_ACCESS_KEY_ID=AKIA...
   AWS_SECRET_ACCESS_KEY=...
   AWS_REGION=us-east-1
   S3_BUCKET_NAME=company-repo-backup
   ```

3. Start backing up:
   ```bash
   repo-backup s3 --github --gitlab --bitbucket
   ```

## Permission Details

### Setup Permissions (Required Once)

These permissions are needed ONLY to run `repo-backup s3 --setup`:

| Permission | Why Needed | When Used |
|------------|------------|-----------|
| `s3:CreateBucket` | Create the backup bucket | Setup only |
| `s3:PutBucketVersioning` | Enable versioning for backup history | Setup only |
| `s3:PutBucketEncryption` | Enable encryption at rest (AES-256) | Setup only |
| `s3:PutBucketPublicAccessBlock` | Block public access for security | Setup only |
| `s3:PutBucketLifecycleConfiguration` | Configure Glacier transitions | Setup only |
| `s3:PutBucketTagging` | Add tags for cost tracking | Setup only |
| `s3:PutBucketPolicy` | Enforce SSL/TLS for uploads | Setup only |
| `s3:GetBucketLocation` | Verify bucket region | Setup + backups |
| `s3:ListBucket` | List bucket contents | Setup + backups |
| `iam:CreateUser` | Create dedicated backup user | Setup only |
| `iam:CreateAccessKey` | Generate access keys for backup user | Setup only |
| `iam:PutUserPolicy` | Attach inline policy to backup user | Setup only |
| `iam:AttachUserPolicy` | Attach managed policy to backup user | Setup only |
| `iam:CreatePolicy` | Create custom S3 policy | Setup only |
| `iam:TagUser` | Add tags to backup user | Setup only |
| `sts:GetCallerIdentity` | Verify AWS credentials | Setup + backups |

### Backup Permissions (Required Daily)

These are the minimal permissions the backup tool uses during daily operations (automatically assigned to `repo-backup-user`):

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "ListBucket",
      "Effect": "Allow",
      "Action": [
        "s3:ListBucket",
        "s3:GetBucketLocation"
      ],
      "Resource": "arn:aws:s3:::BUCKET_NAME"
    },
    {
      "Sid": "ReadWriteObjects",
      "Effect": "Allow",
      "Action": [
        "s3:PutObject",
        "s3:GetObject",
        "s3:DeleteObject",
        "s3:ListBucket"
      ],
      "Resource": "arn:aws:s3:::BUCKET_NAME/*"
    }
  ]
}
```

**Note**: The backup user CANNOT:
- Create or delete buckets
- Modify bucket policies
- Create IAM users
- Access other AWS services

## Security Best Practices

### 1. Use IAM Roles for EC2/ECS

If running backups on AWS infrastructure, use IAM roles instead of access keys:

```bash
# Create role with S3 permissions
aws iam create-role --role-name RepoBackupRole --assume-role-policy-document file://trust-policy.json

# Attach S3 policy
aws iam attach-role-policy --role-name RepoBackupRole --policy-arn arn:aws:iam::aws:policy/AmazonS3FullAccess

# Attach role to EC2 instance
aws ec2 associate-iam-instance-profile --instance-id i-1234567890abcdef0 --iam-instance-profile Name=RepoBackupRole
```

Then no credentials needed in `.env.local` - AWS SDK automatically uses the role.

### 2. Rotate Access Keys Regularly

```bash
# List current keys
aws iam list-access-keys --user-name repo-backup-user

# Create new key
aws iam create-access-key --user-name repo-backup-user

# Update .env.local with new credentials

# Delete old key
aws iam delete-access-key --user-name repo-backup-user --access-key-id AKIA...
```

### 3. Enable MFA for Setup Users

Require MFA for users who have setup permissions:

```json
{
  "Condition": {
    "BoolIfExists": {
      "aws:MultiFactorAuthPresent": "true"
    }
  }
}
```

### 4. Use AWS Organizations SCPs

Prevent creation of buckets outside approved regions:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Deny",
      "Action": "s3:CreateBucket",
      "Resource": "*",
      "Condition": {
        "StringNotEquals": {
          "aws:RequestedRegion": ["us-east-1", "eu-west-1"]
        }
      }
    }
  ]
}
```

### 5. Enable CloudTrail Logging

Monitor all S3 and IAM operations:

```bash
aws cloudtrail create-trail --name repo-backup-audit --s3-bucket-name audit-logs
aws cloudtrail start-logging --name repo-backup-audit
```

### 6. Set Up Bucket Lifecycle Policies

The setup automatically configures lifecycle policies, but you can customize:

```bash
# Standard -> Glacier after 90 days
repo-backup s3 --setup --enable-glacier

# Manual policy
aws s3api put-bucket-lifecycle-configuration --bucket my-backup --lifecycle-configuration file://lifecycle.json
```

Example `lifecycle.json`:
```json
{
  "Rules": [
    {
      "Id": "ArchiveOldBackups",
      "Status": "Enabled",
      "Transitions": [
        {
          "Days": 90,
          "StorageClass": "GLACIER"
        },
        {
          "Days": 365,
          "StorageClass": "DEEP_ARCHIVE"
        }
      ]
    }
  ]
}
```

## Troubleshooting

### Error: "Access Denied" During Setup

**Problem**: User lacks required setup permissions

**Solution**: Ask administrator to attach the `RepoBackupSetupPermissions` policy (see above), or have administrator run setup.

### Error: "Access Denied" During Backup

**Problem**: Backup user lacks S3 permissions

**Solution**:
1. Verify bucket name in `.env.local` matches actual bucket
2. Check IAM policy on backup user includes `s3:PutObject`, `s3:GetObject`
3. Verify credentials are correct

### Error: "Bucket Already Exists"

**Problem**: Bucket name is taken (S3 bucket names are globally unique)

**Solution**: Use a more unique bucket name:
```bash
repo-backup s3 --setup --bucket-name mycompany-repo-backup-$(date +%s)
```

### Error: "Invalid Credentials"

**Problem**: AWS credentials are expired, incorrect, or not configured

**Solution**:
1. Check `.env.local` has correct values
2. Verify access key is active: `aws iam list-access-keys --user-name repo-backup-user`
3. Test credentials: `aws sts get-caller-identity`

### Error: "Bucket in Different Region"

**Problem**: Bucket exists in different region than configured

**Solution**: Ensure `AWS_REGION` in `.env.local` matches bucket region:
```bash
aws s3api get-bucket-location --bucket your-bucket-name
```

## Cost Optimization

### Storage Class Comparison

| Storage Class | Cost (per GB/month) | Use Case |
|---------------|---------------------|----------|
| S3 Standard | $0.023 | Frequently accessed backups |
| S3 Glacier | $0.004 | Long-term archives (90+ days) |
| S3 Glacier Deep Archive | $0.00099 | Compliance/disaster recovery |

### Estimated Costs

For 195 repositories at ~500MB average size:

```
Total size: 195 * 500MB = 97.5GB

S3 Standard: 97.5GB * $0.023 = $2.24/month
S3 Glacier (after 90 days): 97.5GB * $0.004 = $0.39/month

Savings: $1.85/month ($22/year)
```

Enable Glacier during setup:
```bash
repo-backup s3 --setup --enable-glacier
```

### Monitoring Costs

Set up billing alerts:

```bash
aws budgets create-budget --account-id 123456789012 --budget file://budget.json
```

Example `budget.json`:
```json
{
  "BudgetName": "RepoBackupBudget",
  "BudgetLimit": {
    "Amount": "10",
    "Unit": "USD"
  },
  "TimeUnit": "MONTHLY",
  "BudgetType": "COST"
}
```

## Advanced Configuration

### Multi-Region Replication

For disaster recovery, replicate backups to another region:

```bash
# Enable versioning (required for replication)
aws s3api put-bucket-versioning --bucket source-bucket --versioning-configuration Status=Enabled

# Create replication policy
aws s3api put-bucket-replication --bucket source-bucket --replication-configuration file://replication.json
```

### Encryption with KMS

Use customer-managed encryption keys:

```bash
# Create KMS key
aws kms create-key --description "Repo Backup Encryption Key"

# Enable KMS encryption on bucket
aws s3api put-bucket-encryption --bucket my-backup --server-side-encryption-configuration '{
  "Rules": [{
    "ApplyServerSideEncryptionByDefault": {
      "SSEAlgorithm": "aws:kms",
      "KMSMasterKeyID": "arn:aws:kms:us-east-1:123456789012:key/12345678-1234-1234-1234-123456789012"
    }
  }]
}'
```

### VPC Endpoints

For enhanced security, use VPC endpoints to keep traffic within AWS network:

```bash
# Create S3 VPC endpoint
aws ec2 create-vpc-endpoint --vpc-id vpc-12345678 --service-name com.amazonaws.us-east-1.s3 --route-table-ids rtb-12345678
```

## References

- [AWS IAM Best Practices](https://docs.aws.amazon.com/IAM/latest/UserGuide/best-practices.html)
- [S3 Security Best Practices](https://docs.aws.amazon.com/AmazonS3/latest/userguide/security-best-practices.html)
- [S3 Lifecycle Policies](https://docs.aws.amazon.com/AmazonS3/latest/userguide/object-lifecycle-mgmt.html)
- [AWS Cost Optimization](https://aws.amazon.com/pricing/cost-optimization/)
