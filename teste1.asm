section .data
  format_out: db "%d", 10, 0 ; format do printf
  format_in: db "%d", 0 ; format do scanf
  scan_int: dd 0; 32-bits integer

section .text

  extern printf ; usar _printf para Windows
  extern scanf ; usar _scanf para Windows
  ; extern _ExitProcess@4 ; usar para Windows
  global _start ; início do programa

_start:
  push ebp ; guarda o EBP
  mov ebp, esp ; zera a pilha

  ; aqui começa o codigo gerado:

  sub esp, 4 ; var x int [EBP-4]
  mov eax, 3
  mov [ebp-4], eax ; x = 3
  mov eax, 1
  push eax
  mov eax, [ebp-4]
  pop ecx
  add eax, ecx
  push eax ; empilha f
  push format_out ; formato int de saida
  call printf ; Print f
  add esp, 8 ; limpa os argumentos
  mov eax, 1
  mov [ebp-8], eax ; y = 
  mov eax, [ebp-4]
  push eax
  mov eax, [ebp-8]
  pop ecx
  add eax, ecx
  mov [ebp-8], eax ; y = 
  mov eax, [ebp-8]
  push eax ; empilha f
  push format_out ; formato int de saida
  call printf ; Print f
  add esp, 8 ; limpa os argumentos

  ; aqui termina o código gerado

  mov esp, ebp ; reestabelece a pilha
  pop ebp

  ; chamada da interrupcao de saida (Linux)
  mov eax, 1   
  xor ebx, ebx 
  int 0x80     
  ; Para Windows:
  ; push dword 0        
  ; call _ExitProcess@4
