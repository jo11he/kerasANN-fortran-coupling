!compile w/ shared library: 'gfortran -o run_test -L./ -lplugin test_main.f90'

PROGRAM COUPLING_TEST
   use, intrinsic :: iso_c_binding
   implicit none
   interface
      subroutine get_rates(x1, x2, x3, x4, n, y1, y2) bind (c)
         use iso_c_binding
         real*8                        :: x1
         real*8                        :: x2
         real*8                        :: x3
         integer(c_int)                :: n
         real*8                        :: x4(n)
         real*8                        :: y1
         real*8                        :: y2
      end subroutine get_rates
   end interface

   !DECLARE INPUT PARAMETERS
   real*8                              :: T_gas
   real*8                              :: nH
   real*8                              :: n_H

   real*8, allocatable                 :: rf(:)
   integer                             :: rfcount

   !DECLARE OUPUTS
   real*8                              :: LH
   real*8                              :: ER

   !ASSIGN INPUT VALUES (sample 1 of testT01)
   T_gas = 3.911992969999999787e+03
   nH = 5.995181949999999488e+05
   n_H = 6.000000000000000000e+05

	open (unit=1, file='./testrf.txt', status='old', action='read')

		read(1,*) rfcount
		allocate (rf(rfcount))

        read(1,*) rf

	close(1)


   !!!! ACTION !!!!
   PRINT *, rf
   call get_rates(T_gas, nH, n_H, rf, size(rf), LH, ER)
   PRINT *, LH
   PRINT *, ER

   !DESIRED OUTPUT:
   ! LH 1.976698810232987523e-19
   ! ER 9.466660817636688724e-17

END PROGRAM COUPLING_TEST



