"use client";

import { useForm, type UseFormInput, type UseFormReturnType } from "@mantine/form";

export const useDSForm = useForm;

export type DSForm<Values extends object> = UseFormReturnType<Values>;

export type DSFormInput<Values extends object> = UseFormInput<Values>;
