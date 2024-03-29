module.exports = {
  root: true,
  extends: ['@blueking/eslint-config-bk/vue'],
  overrides: [
    {
      files: ['*.js', '*.ts'],
      rules: {
        'no-param-reassign': 'off',
        '@typescript-eslint/no-require-imports': 'off',
        '@typescript-eslint/explicit-member-accessibility': 'off',
      },
    },
  ],
};
