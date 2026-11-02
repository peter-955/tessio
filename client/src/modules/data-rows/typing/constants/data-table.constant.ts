export const MAX_PARAMETERS = 20;

export const MAX_DATA_ROWS = 20;

export const MAX_PARAMETER_NAME_LENGTH = 50;

export const MAX_DATA_VALUE_LENGTH = 1000;

export const PARAMETER_NAME_PATTERN = /^[A-Za-z][A-Za-z0-9_]{0,49}$/;

export const PARAMETER_REFERENCE_PATTERN = /\{\{param\.([A-Za-z][A-Za-z0-9_]*)\}\}/g;

export const PARAMETER_REFERENCE_PREFIX = "{{param.";

export const DATA_REFERENCE_EXAMPLE = "{{data.key}}";
