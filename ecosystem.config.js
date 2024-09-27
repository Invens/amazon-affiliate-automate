module.exports = {
  apps: [
    {
      name: 'dealbot', // First application
      script: '/home/coupleup-deal/htdocs/deal.coupleup.in/amazon-affiliate-automate/app.py',
      interpreter: '/home/coupleup-deal/htdocs/deal.coupleup.in/amazon-affiliate-automate/venv/bin/python',
      watch: true,
      env: {
        FLASK_ENV: 'development',
      },
      env_production: {
        FLASK_ENV: 'production',
      },
    },
    {
      name: 'scheduler', // Second application
      script: '/home/coupleup-deal/htdocs/deal.coupleup.in/amazon-affiliate-automate/campaign_scheduler.py',
      interpreter: '/home/coupleup-deal/htdocs/deal.coupleup.in/amazon-affiliate-automate/venv/bin/python',
      watch: true,
      env: {
        FLASK_ENV: 'development',
      },
      env_production: {
        FLASK_ENV: 'production',
      },
    },
  ],
};
